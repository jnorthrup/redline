#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <openssl/ssl.h>

namespace asio = boost::asio;
using tcp = asio::ip::tcp;

class SSLClient {
public:
    SSLClient(asio::io_context& io_context, asio::ssl::context& context)
        : resolver_(io_context), socket_(io_context, context) {}

    void connect(const std::string& host, const std::string& port) {
        // Resolve the host name
        resolver_.async_resolve(host, port,
            [this](const boost::system::error_code& ec, tcp::resolver::results_type results) {
                if (!ec) {
                    handle_resolve(results);
                } else {
                    std::cerr << "Resolve error: " << ec.message() << "\n";
                }
            });
    }

private:
    void handle_resolve(tcp::resolver::results_type results) {
        // Connect to the server
        asio::async_connect(socket_.lowest_layer(), results,
            [this](const boost::system::error_code& ec, const tcp::endpoint&) {
                if (!ec) {
                    handle_connect();
                } else {
                    std::cerr << "Connect error: " << ec.message() << "\n";
                }
            });
    }

    void handle_connect() {
        // Perform SSL handshake
        socket_.async_handshake(asio::ssl::stream_base::client,
            [this](const boost::system::error_code& ec) {
                if (!ec) {
                    send_request();
                } else {
                    std::cerr << "Handshake error: " << ec.message() << "\n";
                }
            });
    }

    void send_request() {
        // Create proper HTTP GET request
        std::string request = "GET / HTTP/1.1\r\n";
        request += "Host: www.google.com\r\n";
        request += "User-Agent: SSLClient/1.0\r\n";
        request += "Accept: */*\r\n";
        request += "Connection: close\r\n\r\n";

        // Send the request
        asio::async_write(socket_, asio::buffer(request),
            [this](const boost::system::error_code& ec, std::size_t) {
                if (!ec) {
                    receive_response();
                } else {
                    std::cerr << "Write error: " << ec.message() << "\n";
                }
            });
    }

    void receive_response() {
        // Read the response with error handling
        asio::async_read(socket_, response_, asio::transfer_at_least(1),
            [this](const boost::system::error_code& ec, std::size_t length) {
                if (!ec) {
                    std::cout << &response_;
                    receive_response(); // Continue reading
                } else if (ec == asio::error::eof) {
                    // Connection closed by server
                    std::cout << "Connection closed by server\n";
                } else {
                    std::cerr << "Read error: " << ec.message() << "\n";
                }
            });
    }

    tcp::resolver resolver_;
    asio::ssl::stream<tcp::socket> socket_;
    asio::streambuf response_;
};

int main() {
    try {
        asio::io_context io_context;

        // Set up SSL context with modern settings
        asio::ssl::context ctx(asio::ssl::context::tlsv13_client);
        ctx.set_default_verify_paths();
        ctx.set_verify_mode(asio::ssl::verify_peer | asio::ssl::verify_fail_if_no_peer_cert);
        
        // Set modern TLS options
        SSL_CTX_set_options(ctx.native_handle(), 
            SSL_OP_ALL | SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | 
            SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);
        
        // Set secure cipher list
        SSL_CTX_set_cipher_list(ctx.native_handle(), 
            "HIGH:!aNULL:!MD5:!RC4:!SHA1:!SHA256:!SHA384");

        SSLClient client(io_context, ctx);
        client.connect("www.google.com", "443");

        io_context.run();
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
    }

    return 0;
}
