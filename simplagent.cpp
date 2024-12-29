#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/beast.hpp>
#include <boost/beast/ssl.hpp>
#include <boost/json.hpp>
#include <iostream>
#include <string>
#include <memory>
#include <iomanip>
#include <chrono>
#include <map>
#include <fstream>

namespace beast = boost::beast;
namespace http = beast::http;
namespace json = boost::json;

struct ProviderConfig {
    std::string endpoint;
    // Add other provider-specific configuration here
};

int main() {
    try {
        asio::io_context ioc;
        std::string provider = "OPENROUTER"; // Hardcoded provider for now
        std::string model = "gpt-3.5-turbo"; // Example model
        std::string api_key = get_api_key(provider);
        if (api_key.empty()) {
            std::cerr << "API key for " << provider << " not found. Please set the environment variable " << provider << "_API_KEY or create api_key.txt." << std::endl;
            return 1;
        }

        SimplAgent agent(ioc, api_key, provider, model);
        agent.start();
        ioc.run();
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}

std::string get_api_key(const std::string& provider) {
    // Convert provider name to uppercase for environment variable
    std::string env_var = provider;
    std::transform(env_var.begin(), env_var.end(), env_var.begin(), ::toupper);
    env_var += "_API_KEY";
    
    // Get API key from environment
    const char* api_key = std::getenv(env_var.c_str());
    if (api_key && strlen(api_key) > 0) {
        return std::string(api_key);
    }
    
    // Check for common API key locations
    std::vector<std::string> key_paths = {
        "/usr/local/etc/" + provider + "/api_key",
        "/opt/homebrew/etc/" + provider + "/api_key",
        std::string(getenv("HOME")) + "/." + provider + "/api_key"
    };
    
    for (const auto& path : key_paths) {
        std::ifstream key_file(path);
        if (key_file) {
            std::string key;
            std::getline(key_file, key);
            if (!key.empty()) {
                return key;
            }
        }
    }
    
    // Check for local api_key.txt file
    std::ifstream local_key_file("api_key.txt");
    if (local_key_file) {
        std::string key;
        std::getline(local_key_file, key);
        if (!key.empty()) {
            return key;
        }
    }
    
    return ""; // Return empty string if no key found
}

const std::map<std::string, ProviderConfig> PROVIDER_CONFIGS = {
    {"OPENROUTER", {"openrouter.ai"}}
    // Add other provider configurations here
};

// Constants
constexpr int SSL_READ_BUFFER_SIZE = 4096;
constexpr int SSL_HANDSHAKE_TIMEOUT = 10; // seconds
constexpr int SSL_READ_TIMEOUT = 30; // seconds

namespace asio = boost::asio;
using tcp = asio::ip::tcp;

class SimplAgent {
private:
    asio::io_context& ioc_;
    asio::steady_timer timer_;
    std::string api_key_;
    std::string provider_;
    ProviderConfig provider_config_;
    std::string current_input_;
    std::vector<json::value> conversation_;
    std::string model_;
    asio::ssl::context ssl_ctx_;
    beast::flat_buffer buffer_;

public:
    SimplAgent(asio::io_context& ioc, const std::string& api_key, const std::string& provider, const std::string& model)
        : ioc_(ioc), 
          timer_(ioc), 
          api_key_(api_key), 
          provider_(provider), 
          model_(model), 
          ssl_ctx_(asio::ssl::context::tlsv13_client) {
        
        auto it = PROVIDER_CONFIGS.find(provider);
        if (it == PROVIDER_CONFIGS.end()) {
            throw std::runtime_error("Invalid provider: " + provider);
        }
        provider_config_ = it->second;

        // Configure SSL context with modern settings
        std::cerr << "Using OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << "\n";
        ssl_ctx_.set_default_verify_paths();
        ssl_ctx_.set_verify_mode(asio::ssl::verify_peer | asio::ssl::verify_fail_if_no_peer_cert);
        
        // Set modern TLS options
        SSL_CTX_set_options(ssl_ctx_.native_handle(), 
            SSL_OP_ALL | SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | 
            SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);
        
        // Set secure cipher list
        SSL_CTX_set_cipher_list(ssl_ctx_.native_handle(), 
            "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256");
        std::cerr << "SSL context configured with modern TLS settings\n";
        
        // macOS-specific SSL configuration
        #ifdef __APPLE__
            // Use system's default certificate store
            ssl_ctx_.set_default_verify_paths();
            // Set macOS-specific SSL options
            SSL_CTX_set_options(ssl_ctx_.native_handle(), SSL_OP_ALL | SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3);
            // Load system certificates with error handling
            std::vector<std::string> cert_paths = {
                "/etc/ssl/cert.pem",
                "/usr/local/etc/openssl@3/cert.pem",
                "/opt/homebrew/etc/openssl@3/cert.pem"
            };
            
            bool certs_loaded = false;
            for (const auto& path : cert_paths) {
                // Detailed file access check
                struct stat file_stat;
                if (stat(path.c_str(), &file_stat) == 0) {
                    std::cerr << "Certificate file found: " << path << "\n";
                    std::cerr << "File size: " << file_stat.st_size << " bytes\n";
                    std::cerr << "Permissions: " << std::oct << file_stat.st_mode << std::dec << "\n";
                    
                    if (file_stat.st_size == 0) {
                        std::cerr << "Warning: Certificate file is empty\n";
                        continue;
                    }

                    if (access(path.c_str(), R_OK) != 0) {
                        std::cerr << "Warning: Certificate file not readable\n";
                        std::cerr << "Access error: " << strerror(errno) << "\n";
                        continue;
                    }

                    // Try loading using SSL_CTX_load_verify_locations
                    if (SSL_CTX_load_verify_locations(ssl_ctx_.native_handle(), path.c_str(), nullptr) == 1) {
                        std::cerr << "Successfully loaded certificates from: " << path << "\n";
                        certs_loaded = true;
                        break;
                    } else {
                        std::cerr << "Warning: Failed to load certificates from " << path << "\n";
                        std::cerr << "SSL error: " << ERR_error_string(ERR_get_error(), nullptr) << "\n";
                    }
                } else {
                    std::cerr << "Warning: Certificate file " << path << " not found\n";
                    std::cerr << "Stat error: " << strerror(errno) << "\n";
                }
            }
            
            if (!certs_loaded) {
                std::cerr << "Warning: No certificate files found, using default system certificates\n";
                ssl_ctx_.set_default_verify_paths();
            }
        #endif
        
        // Enable detailed SSL debugging
        SSL_CTX_set_info_callback(ssl_ctx_.native_handle(), [](const SSL* ssl, int where, int ret) {
            if (where & SSL_CB_ALERT) {
                std::cerr << "SSL Alert: " << SSL_alert_desc_string_long(ret) << "\n";
            }
            if (where & SSL_CB_HANDSHAKE_START) {
                std::cerr << "Handshake started\n";
            }
            if (where & SSL_CB_HANDSHAKE_DONE) {
                std::cerr << "Handshake completed\n";
            }
        });
    }

    void start() {
        std::cout << "Starting chat (type 'exit' to quit)...\n";
        prompt_input();
    }

private:
    void prompt_input() {
        std::cout << "\nYou: ";
        std::getline(std::cin, current_input_);
        
        if (current_input_ == "exit") {
            std::cout << "Chat session ended.\n";
            return;
        }

        start_debounce();
    }

    void start_debounce() {
        timer_.expires_after(std::chrono::milliseconds(250));
        timer_.async_wait([this](const boost::system::error_code& ec) {
            if (!ec) {
                process_input();
            }
        });
    }

    void process_input() {
        if (current_input_.empty()) {
            prompt_input();
            return;
        }

        conversation_.emplace_back(json::object{
            {"role", "user"},
            {"content", current_input_}
        });

        make_request();
    }

    void make_request() {
        auto req = std::make_shared<http::request<http::string_body>>();
        req->method(http::verb::post);
        req->target("/api/v1/chat/completions");
        req->set(http::field::host, provider_config_.endpoint);
        req->set(http::field::authorization, "Bearer " + api_key_);
        req->set(http::field::content_type, "application/json");
        req->set("HTTP-Referer", "http://localhost:8000");
        req->set("X-Title", "CLI Chat");

        json::array messages;
        for (const auto& msg : conversation_) {
            messages.push_back(msg);
        }
        
        json::value body = {
            {"model", model_},
            {"messages", messages},
            {"temperature", 0.7}
        };
        req->body() = json::serialize(body);
        req->prepare_payload();

        auto resolver = std::make_shared<tcp::resolver>(ioc_);
        resolver->async_resolve(provider_config_.endpoint, "https",
            [this, req, resolver](const boost::system::error_code& ec,
                                tcp::resolver::results_type results) {
                if (ec) {
                    std::cerr << "Resolve error: " << ec.message() << "\n";
                    return;
                }
                connect_and_send(req, results);
            });
    }

    void connect_and_send(std::shared_ptr<http::request<http::string_body>> req,
                        tcp::resolver::results_type results) {
        auto stream = std::make_shared<beast::ssl_stream<beast::tcp_stream>>(ioc_, ssl_ctx_);
        std::cerr << "Connecting to: " << provider_config_.endpoint << "\n";
        beast::get_lowest_layer(*stream).async_connect(results,
            [this, req, stream](const boost::system::error_code& ec,
                              tcp::resolver::results_type::endpoint_type) {
                if (ec) {
                    std::cerr << "Connect error: " << ec.message() << "\n";
                    return;
                }
                std::cerr << "Handshake starting...\n";
                
                // Set handshake timeout with retry logic
                auto handshake_timer = std::make_shared<asio::steady_timer>(ioc_);
                handshake_timer->expires_after(std::chrono::seconds(30));
                
                std::function<void(const boost::system::error_code&)> handshake_handler;
                handshake_handler = [this, req, stream, handshake_timer, &handshake_handler](const boost::system::error_code& ec) {
                    if (ec) {
                        if (ec == asio::error::would_block || ec == asio::error::try_again) {
                            // Retry handshake after short delay
                            std::cerr << "Handshake would block, retrying...\n";
                            auto retry_timer = std::make_shared<asio::steady_timer>(ioc_);
                            retry_timer->expires_after(std::chrono::milliseconds(100));
                            retry_timer->async_wait([this, req, stream, handshake_timer, &handshake_handler](const boost::system::error_code& ec) {
                                if (!ec) {
                                    stream->async_handshake(asio::ssl::stream_base::client, handshake_handler);
                                }
                            });
                            return;
                        }
                        
                        std::cerr << "Handshake error: " << ec.message() << "\n";
                        std::cerr << "SSL error: " << ec.category().name() << " - " << ec.value() << "\n";
                        std::cerr << "SSL error string: " << ERR_error_string(ERR_get_error(), nullptr) << "\n";
                        std::cerr << "SSL shutdown state: " << SSL_get_shutdown(stream->native_handle()) << "\n";
                        return;
                    }
                    
                    handshake_timer->cancel();
                    std::cerr << "Handshake successful\n";
                    std::cerr << "SSL version: " << SSL_get_version(stream->native_handle()) << "\n";
                    std::cerr << "Cipher: " << SSL_get_cipher(stream->native_handle()) << "\n";
                    http::async_write(*stream, *req,
                        [this, req, stream](const boost::system::error_code& ec,
                                          std::size_t) {
                            if (ec) {
                                std::cerr << "Write error: " << ec.message() << "\n";
                                std::cerr << "SSL error: " << ec.category().name() << " - " << ec.value() << "\n";
                                return;
                            }
                            receive_response(stream);
                        });
                };

                handshake_timer->async_wait([stream](const boost::system::error_code& ec) {
                    if (!ec) {
                        std::cerr << "Handshake timeout\n";
                        beast::get_lowest_layer(*stream).close();
                    }
                });

                stream->async_handshake(asio::ssl::stream_base::client, handshake_handler);
            });
    }

    void receive_response(std::shared_ptr<beast::ssl_stream<beast::tcp_stream>> stream) {
        auto res = std::make_shared<http::response<http::string_body>>();
        http::async_read(*stream, buffer_, *res,
            [this, stream, res](const boost::system::error_code& ec,
                              std::size_t) {
                if (ec) {
                    std::cerr << "Read error: " << ec.message() << "\n";
                    return;
                }
                process_response(res->body());
                prompt_input();
            });
    }

    void process_response(const std::string& response) {
        try {
            auto json = json::parse(response);
            if (json.is_object() && json.as_object().contains("choices")) {
                auto choices = json.at("choices");
                if (choices.is_array() && choices.as_array().size() > 0) {
                    auto choice = choices.at(0);
                    if (choice.is_object() && choice.as_object().contains("message")) {
                        auto message = choice.at("message");
                        if (message.is_object() && message.as_object().contains("content")) {
                            auto content = message.at("content").as_string();
                            std::cout << "\nAssistant: " << content << "\n";
                            conversation_.emplace_back(json::object{
                                {"role", "assistant"},
                                {"content", content}
                            });
                        } else {
                            std::cerr << "Error: 'message' does not contain 'content'\n";
                        }
                    } else {
                        std::cerr << "Error: 'choice' is not an object or does not contain 'message'\n";
                    }
                } else {
                    std::cerr << "Error: 'choices' is not an array or is empty\n";
                }
            } else {
                std::cerr << "Error: 'choices' not found in response\n";
            }
        } catch (const std::exception& e) {
            std::cerr << "Error parsing response: " << e.what() << "\n";
        }
    }
};
