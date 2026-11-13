
import socket
import ipaddress

from concurrent.futures import ThreadPoolExecutor, as_completed


def grab_banner(target_ip, port):

    sock = None
    connected = False

    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set timeout
        sock.settimeout(5)

        # Connect to target
        sock.connect((target_ip, port))
        connected = True

        # Send HTTP request for web ports
        if port in [80, 8080]:

            request = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {target_ip}\r\n"
                f"Connection: close\r\n\r\n"
            )

            sock.sendall(request.encode("utf-8"))

        # Receive banner
        banner = sock.recv(1024)

        # Decode received data
        banner = banner.decode("utf-8", errors="ignore")

        # Extract first line
        if banner.strip():

            first_line = banner.splitlines()[0]

            return port, "OPEN", first_line

        return port, "OPEN", "No Banner Received"

    except socket.timeout:

        if connected:
            return port, "OPEN", "No Banner (Timeout)"

        return port, "TIMEOUT", "Connection timed out"

    except OSError:

        return port, "CLOSED", "Connection failed"

    finally:

        if sock is not None:
            sock.close()


def main():

    # Get target IP from user
    target_ip = input("Enter Target IP: ").strip()

    # Validate IP address
    try:
        ipaddress.ip_address(target_ip)

    except ValueError:
        print("Invalid IP Address!")
        return

    # Define ports
    ports = [135, 139, 445, 623, 903, 913,5050]

    print(f"\nStarting Banner Grabber: {target_ip}\n")

    # Scan ports using threads
    with ThreadPoolExecutor(max_workers=20) as executor:

        futures = [
            executor.submit(grab_banner, target_ip, port)
            for port in ports
        ]

        for future in as_completed(futures):

            port, status, banner = future.result()

            if status == "OPEN":

                print(f"[+] Port {port} - OPEN")
                print(f"    Banner: {banner}\n")

            elif status == "TIMEOUT":

                print(f"[!] Port {port} - TIMEOUT\n")

    print("Scan Completed!")


if __name__ == "__main__":
    main()
