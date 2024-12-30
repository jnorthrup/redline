#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/asio/experimental/awaitable_operators.hpp>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <map>
#include <vector>

namespace net = boost::asio;
namespace ssl = net::ssl;
using tcp = net::ip::tcp;
using namespace net::experimental::awaitable_operators;

struct ProviderConfig {
    std::string endpoint;
    std::vector<std::string> models;
};

const std::map<std::string, ProviderConfig> PROVIDER_CONFIGS = {
    {"ANTHROPIC", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
    {"GEMINI", {"https://generativelanguage.googleapis.com/v1beta", {"gemini-pro", "gemini-pro-vision", "gemini-ultra", "gemini-nano"}}},
    {"OPENAI", {"https://api.openai.com/v1", {"gpt-4", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"}}},
    {"PERPLEXITY", {"https://api.perplexity.ai", {"llama-3.1-sonar-huge-128k-online", "llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online", "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"}}},
    {"GROK", {"https://api.x.ai", {"grok-2-1212", "grok-2-vision-1212", "grok-beta", "grok-vision-beta"}}},
    {"DEEPSEEK", {"https://api.deepseek.com", {"deepseek-ai/DeepSeek-V2-Chat", "deepseek-ai/DeepSeek-V2", "deepseek-ai/DeepSeek-67B", "deepseek-ai/DeepSeek-13B"}}},
    {"CLAUDE", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
    {"OPENROUTER", {"https://openrouter.ai/api/v1", {"openrouter/auto", "openrouter/default", "openrouter/grok", "openrouter/claude"}}},
    {"HUGGINGFACE", {"https://api-inference.huggingface.co", {"meta-llama/Meta-Llama-3-8B-Instruct", "google/flan-t5-xxl", "EleutherAI/gpt-neo-2.7B", "bigscience/bloom-7b1"}}}
};

class SSLClient {
private:
    tcp::resolver resolver_;
    asio::ssl::stream<tcp::socket> socket_;
    std::string host_;
    asio::streambuf response_;

public:
    SSLClient(asio::io_context& io_context, asio::ssl::context& context)
        : resolver_(io_context), socket_(io_context, context), host_("") {}

    net::awaitable<void> connect(const std::string& host, const std::string& port) {
        host_ = host;
        auto [ec, results] = co_await resolver_.async_resolve(host, port, net::use_awaitable);
        if (ec) {
            std::cerr << "Resolve error: " << ec.message() << "\n";
            co_return;
        }
        co_await handle_resolve(results);
    }

    bool is_connected() const {
        return socket_.lowest_layer().is_open();
    }

    net::awaitable<void> get_model_info(const std::string& provider) {
        try {
            if (!socket_.lowest_layer().is_open()) {
                throw std::runtime_error("Socket is not open");
            }

            std::string request = "GET /models HTTP/1.1\r\n";
            request += "Host: " + PROVIDER_CONFIGS.at(provider).endpoint + "\r\n";
            request += "User-Agent: SSLClient/1.0\r\n";
            request += "Accept: application/json\r\n";
            request += "Connection: close\r\n\r\n";

            co_await asio::async_write(socket_, asio::buffer(request), net::use_awaitable);
            co_await receive_response();
        } catch (const std::exception& e) {
            std::cerr << "Error in get_model_info: " << e.what() << "\n";
            throw;
        }
    }

private:
    net::awaitable<void> handle_resolve(tcp::resolver::results_type results) {
        auto [ec, endpoint] = co_await asio::async_connect(socket_.lowest_layer(), results, net::use_awaitable);
        if (ec) {
            std::cerr << "Connect error: " << ec.message() << "\n";
            co_return;
        }
        co_await handle_connect();
    }

    net::awaitable<void> handle_connect() {
        void* native_handle = socket_.native_handle();
        if (!native_handle) {
            std::cerr << "Failed to get native SSL handle\n";
            co_return;
        }
        
        SSL* ssl_handle = reinterpret_cast<SSL*>(native_handle);
        if (!ssl_handle) {
            std::cerr << "Failed to cast native handle to SSL pointer\n";
            co_return;
        }
        
        if (!SSL_set_tlsext_host_name(ssl_handle, host_.c_str())) {
            std::cerr << "Failed to set SNI hostname\n";
            co_return;
        }

        if (!socket_.lowest_layer().is_open()) {
            std::cerr << "Socket is not open\n";
            co_return;
        }

        boost::system::error_code ec;
        auto endpoint = socket_.lowest_layer().remote_endpoint(ec);
        if (ec) {
            std::cerr << "Failed to get remote endpoint: " << ec.message() << "\n";
        } else {
            std::cout << "Connected to " << endpoint.address().to_string() 
                      << ":" << endpoint.port() << "\n";
        }

        co_await socket_.async_handshake(asio::ssl::stream_base::client, net::use_awaitable);
        co_await send_request();
    }

    net::awaitable<void> send_request() {
        std::string request = "POST /chat/completions HTTP/1.1\r\n";
        request += "Host: api.deepseek.com\r\n";
        request += "User-Agent: SSLClient/1.0\r\n";
        request += "Accept: application/json\r\n";
        request += "Content-Type: application/json\r\n";
        
        std::string env_var = "DEEPSEEK_API_KEY";
        const char* api_key = std::getenv(env_var.c_str());
        if (!api_key || strlen(api_key) == 0) {
            std::string provider_upper = "DEEPSEEK";
            std::transform(provider_upper.begin(), provider_upper.end(), provider_upper.begin(), ::toupper);
            std::vector<std::string> key_vars = {
                provider_upper + "_API_KEY",
                "OPENROUTER_API_KEY",
                "API_KEY"
            };
            
            for (const auto& key : key_vars) {
                api_key = std::getenv(key.c_str());
                if (api_key && strlen(api_key) > 0) {
                    break;
                }
            }
            
            if (!api_key || strlen(api_key) == 0) {
                std::cerr << "Error: API key not found. Please set " << provider_upper << "_API_KEY environment variable\n";
                co_return;
            }
        }
        request += "Authorization: Bearer " + std::string(api_key) + "\r\n";
        request += "Connection: close\r\n";
        
        std::string json_body = R"({
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7
        })";
        
        request += "Content-Length: " + std::to_string(json_body.length()) + "\r\n\r\n";
        request += json_body;

        co_await asio::async_write(socket_, asio::buffer(request), net::use_awaitable);
        co_await receive_response();
    }

    net::awaitable<void> receive_response() {
        try {
            while (true) {
                std::size_t length = co_await asio::async_read(socket_, response_, asio::transfer_at_least(1), net::use_awaitable);
                std::cout << &response_;
            }
        } catch (const boost::system::system_error& e) {
            if (e.code() == asio::error::eof) {
                std::cout << "Connection closed by server\n";
            } else {
                std::cerr << "Read error: " << e.what() << "\n";
            }
        }
    }
};

struct ErrorData {
    std::string timestamp;
    std::string error_type;
    std::string provider;
    std::string endpoint;
    std::string details;
};

class ErrorInstrumentation {
public:
    static void record_error(const ErrorData& data) {
        errors.push_back(data);
    }

    static std::vector<ErrorData> get_errors() {
        return errors;
    }

private:
    static std::vector<ErrorData> errors;
};

std::vector<ErrorData> ErrorInstrumentation::errors;

int main(int argc, char* argv[]) {
    bool enable_fallback = true;
    bool verbose_logging = false;
    std::string primary_provider = "DEEPSEEK";
    std::string fallback_provider = "GEMINI";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--no-fallback") {
            enable_fallback = false;
        } else if (arg == "--verbose") {
            verbose_logging = true;
        } else if (arg == "--provider" && i + 1 < argc) {
            primary_provider = argv[++i];
        } else if (arg == "--fallback" && i + 1 < argc) {
            fallback_provider = argv[++i];
        }
    }

    try {
        asio::io_context io_context;
        asio::ssl::context ctx(asio::ssl::context::tls_client);
        
        ctx.set_default_verify_paths();
        ctx.set_verify_mode(asio::ssl::verify_peer | asio::ssl::verify_fail_if_no_peer_cert);
        ctx.set_verify_callback([](bool preverified, boost::asio::ssl::verify_context& verify_ctx) {
            if (!preverified) {
                X509* cert = X509_STORE_CTX_get_current_cert(verify_ctx.native_handle());
                char buf[256];
                X509_NAME_oneline(X509_get_subject_name(cert), buf, sizeof(buf));
                std::cerr << "Certificate verification failed for: " << buf << "\n";
                return false;
            }
            return true;
        });
        
        SSL_CTX_set_min_proto_version(ctx.native_handle(), TLS1_2_VERSION);
        SSL_CTX_set_max_proto_version(ctx.native_handle(), TLS1_3_VERSION);
        
        SSL_CTX_set_cipher_list(ctx.native_handle(), 
            "ECDHE-ECDSA-AES128-GCM-SHA256:"
            "ECDHE-RSA-AES128-GCM-SHA256:"
            "ECDHE-ECDSA-AES256-GCM-SHA384:"
            "ECDHE-RSA-AES256-GCM-SHA384:"
            "ECDHE-ECDSA-CHACHA20-POLY1305:"
            "ECDHE-RSA-CHACHA20-POLY1305:"
            "DHE-RSA-AES128-GCM-SHA256:"
            "DHE-RSA-AES256-GCM-SHA384");
        
        SSL_CTX_set_options(ctx.native_handle(),
            SSL_OP_ALL | SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | 
            SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);

        auto try_provider = [&](const std::string& provider) -> bool {
            try {
                if (PROVIDER_CONFIGS.find(provider) == PROVIDER_CONFIGS.end()) {
                    throw std::runtime_error("Unknown provider: " + provider);
                }
                const auto& config = PROVIDER_CONFIGS.at(provider);
                
                std::string host = config.endpoint;
                size_t pos = host.find("://");
                if (pos != std::string::npos) {
                    host = host.substr(pos + 3);
                }
                pos = host.find('/');
                if (pos != std::string::npos) {
                    host = host.substr(0, pos);
                }
                
                SSLClient client(io_context, ctx);
                if (verbose_logging) {
                    std::cout << "Connecting to " << host << ":443...\n";
                }
                client.connect(host, "443");
                
                if (!client.is_connected()) {
                    std::string error_msg = "Failed to establish connection to " + host;
                    if (verbose_logging) {
                        error_msg += "\nCheck network connectivity and SSL/TLS configuration";
                    }
                    throw std::runtime_error(error_msg);
                } else if (verbose_logging) {
                    std::cout << "Successfully connected to " << host << "\n";
                    std::cout << "HTTP status codes are not considered errors\n";
                }
                if (verbose_logging) {
                    std::cout << "Successfully connected to " << host << "\n";
                }
                
                client.get_model_info(provider);

                io_context.run();
                return true;
            } catch (const std::exception& e) {
                ErrorData error{
                    .timestamp = std::to_string(std::time(nullptr)),
                    .error_type = "ConnectionError",
                    .provider = provider,
                    .endpoint = PROVIDER_CONFIGS.at(provider).endpoint,
                    .details = e.what()
                };
                ErrorInstrumentation::record_error(error);

                if (verbose_logging) {
                    std::cerr << "Error with provider " << provider << ": " << e.what() << "\n";
                }
                
                std::cout << "\nRunning enhanced diagnostic checks...\n";
                
                std::string curl_cmd = "curl -v " + PROVIDER_CONFIGS.at(provider).endpoint;
                std::cout << "Executing: " << curl_cmd << "\n";
                int curl_result = std::system(curl_cmd.c_str());
                std::cout << "Curl exit code: " << curl_result << "\n";
                
                std::string google_test = "curl -v https://google.com";
                std::cout << "Executing: " << google_test << "\n";
                int google_result = std::system(google_test.c_str());
                std::cout << "Google.com test exit code: " << google_result << "\n";
                
                std::cout << "\nFallback test results:\n";
                std::cout << "Provider curl vs Google fallback: " 
                          << ((curl_result == google_result) ? "Same" : "Different") << "\n";
                
                return false;
            }
        };

        if (!try_provider(primary_provider) && enable_fallback) {
            std::cout << "Attempting fallback to provider: " << fallback_provider << "\n";
            try_provider(fallback_provider);
        }

        const auto& errors = ErrorInstrumentation::get_errors();
        if (!errors.empty()) {
            std::cout << "\nEncountered " << errors.size() << " errors:\n";
            for (const auto& error : errors) {
                std::cout << "[" << error.timestamp << "] " << error.provider 
                          << " (" << error.endpoint << "): " << error.details << "\n";
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
