"""Background job to perform a DNS lookup and insert into or update in the db.

Attributes:
    DNS_SERVERS: A list of strs representing which DNS servers to use
    DNS_BLOCKLIST: A str representing the blocklist to send a DNS lookup to
"""

import dns.resolver

from models import IPDetails, ResponseCode

# Spamhaus will not work with Google's public DNS servers
# https://www.spamhaus.org/faq/section/DNSBL%20Usage#261
DNS_SERVERS = ["208.67.222.222"]  # OpenDNS
DNS_BLOCKLIST = "zen.spamhaus.org"


def upsert_ip_details(ip_address):
    """Insert or update an IPDetails record in the db.

    Args:
        ip_address: A str representing the record in the db to insert or update
    """
    response_codes = dns_lookup(ip_address)
    ip_details = IPDetails.query.filter_by(ip_address=ip_address).first()
    if ip_details is None:
        ip_details = IPDetails(
            response_codes=response_codes, ip_address=ip_address
        )
        ip_details.insert()
    else:
        ip_details.response_codes = response_codes
        ip_details.update()


def dns_lookup(ip_address):
    """Perform a DNS lookup of an IP address to a blocklist.

    Args:
        ip_address: A str representing the ip address to perform a DNS lookup
            against a blocklist

    Returns:
        response_codes: A list of ResponseCode objects representing the
            returned response codes from the DNS lookup against a blocklist
    """
    ip_address = ip_address.split(".")
    if len(ip_address) != 4 or not all(num.isnumeric() for num in ip_address):
        raise TypeError("Incorrect format for IPv4 IP Address")

    ip_address = ".".join(reversed(ip_address))
    response_codes = []
    dns.resolver.get_default_resolver().nameservers = DNS_SERVERS
    try:
        answer = dns.resolver.resolve(f"{ip_address}.{DNS_BLOCKLIST}")
    except dns.resolver.NXDOMAIN:
        return response_codes

    for data in answer:
        response_code = ResponseCode.query.filter_by(
            response_code=str(data)
        ).first()
        if response_code is None:
            response_code = ResponseCode(response_code=str(data))
            response_code.insert()

        response_codes.append(response_code)

    return response_codes
