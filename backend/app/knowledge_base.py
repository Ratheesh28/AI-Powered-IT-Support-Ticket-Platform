
"""Curated knowledge base articles for IT support troubleshooting."""

KNOWLEDGE_BASE = [
    # Network articles
    {
        "id": 1,
        "title": "Troubleshooting Wi-Fi Connectivity Issues",
        "category": "Network",
        "keywords": ["wifi", "wi-fi", "wireless", "internet", "connectivity", "network"],
        "content": "Check whether Wi-Fi is enabled, verify the network password, restart the router, and reconnect to the network.",
        "steps": [
            "Check that Wi-Fi is enabled on your device.",
            "Verify that you are connecting to the correct network.",
            "Restart your router and device.",
            "Reconnect and test the internet connection."
        ]
    },
    {
        "id": 2,
        "title": "Resolving VPN Connection Problems",
        "category": "Network",
        "keywords": ["vpn", "remote access", "timeout", "connection", "tunnel"],
        "content": "Verify internet connectivity, check VPN credentials, restart the VPN client, and reconnect.",
        "steps": [
            "Confirm that your internet connection works.",
            "Verify your VPN username and credentials.",
            "Restart the VPN application.",
            "Reconnect to the VPN server."
        ]
    },
    {
        "id": 3,
        "title": "Basic DNS Troubleshooting",
        "category": "Network",
        "keywords": ["dns", "website", "domain", "server", "resolution"],
        "content": "Check DNS resolution, flush the local DNS cache, and verify the configured DNS server.",
        "steps": [
            "Check whether the website is reachable from another device.",
            "Flush the local DNS cache.",
            "Verify the configured DNS server.",
            "Retry the connection."
        ]
    },

    # Hardware articles
    {
        "id": 4,
        "title": "Laptop Not Powering On",
        "category": "Hardware",
        "keywords": ["laptop", "power", "boot", "startup", "battery"],
        "content": "Check the power adapter, charging indicator, battery, and perform a basic power reset.",
        "steps": [
            "Check whether the power adapter is properly connected.",
            "Inspect the charging indicator.",
            "Disconnect peripherals and try restarting.",
            "If the issue continues, contact hardware support."
        ]
    },
    {
        "id": 5,
        "title": "Printer Connectivity and Printing Issues",
        "category": "Hardware",
        "keywords": ["printer", "printing", "paper", "print", "device"],
        "content": "Verify printer power, cable or network connectivity, paper supply, and printer queue.",
        "steps": [
            "Check that the printer is powered on.",
            "Verify USB or network connectivity.",
            "Check paper and ink or toner levels.",
            "Clear stuck print jobs and retry."
        ]
    },
    {
        "id": 6,
        "title": "Keyboard and Mouse Troubleshooting",
        "category": "Hardware",
        "keywords": ["keyboard", "mouse", "usb", "input", "peripheral"],
        "content": "Check USB or wireless connections, replace batteries if needed, and test another port.",
        "steps": [
            "Reconnect the keyboard or mouse.",
            "Try another USB port if applicable.",
            "Check wireless batteries and pairing.",
            "Test the device on another computer."
        ]
    },

    # Software articles
    {
        "id": 7,
        "title": "Application Crashing or Not Responding",
        "category": "Software",
        "keywords": ["application", "app", "crash", "software", "freeze", "not responding"],
        "content": "Restart the application, check system resources, install available updates, and review error messages.",
        "steps": [
            "Close and reopen the application.",
            "Check available memory and system resources.",
            "Install available application updates.",
            "Record any error message if the issue continues."
        ]
    },
    {
        "id": 8,
        "title": "Software Installation Troubleshooting",
        "category": "Software",
        "keywords": ["install", "installation", "setup", "update", "software"],
        "content": "Verify system requirements, installation permissions, available disk space, and installer integrity.",
        "steps": [
            "Check whether your device meets the software requirements.",
            "Verify that you have installation permissions.",
            "Check available disk space.",
            "Download the installer from an approved source."
        ]
    },
    {
        "id": 9,
        "title": "Operating System Update Problems",
        "category": "Software",
        "keywords": ["windows", "update", "operating system", "os", "upgrade"],
        "content": "Check internet connectivity, available disk space, and restart the device before retrying the update.",
        "steps": [
            "Check your internet connection.",
            "Ensure sufficient free disk space.",
            "Restart the computer.",
            "Retry the update and record any error code."
        ]
    },

    # Account Access articles
    {
        "id": 10,
        "title": "Password Reset and Account Recovery",
        "category": "Account Access",
        "keywords": ["password", "reset", "forgot", "credentials", "login"],
        "content": "Use the approved password recovery process and verify your identity before resetting credentials.",
        "steps": [
            "Open your organization's approved password recovery portal.",
            "Complete the identity verification process.",
            "Set a new password following company policy.",
            "Sign in again with the updated credentials."
        ]
    },
    {
        "id": 11,
        "title": "Resolving Account Lockout Issues",
        "category": "Account Access",
        "keywords": ["locked", "lockout", "account", "login", "authentication"],
        "content": "Verify the account lockout message and follow the organization's approved account unlock procedure.",
        "steps": [
            "Confirm that the account is locked.",
            "Stop repeated login attempts.",
            "Use the approved account unlock process.",
            "Contact IT support if access is not restored."
        ]
    },
    {
        "id": 12,
        "title": "Multi-Factor Authentication Troubleshooting",
        "category": "Account Access",
        "keywords": ["mfa", "2fa", "otp", "authentication", "verification", "authenticator"],
        "content": "Verify device time, network connectivity, and authenticator configuration. Never share verification codes.",
        "steps": [
            "Check that your phone has internet connectivity.",
            "Verify that the device date and time are correct.",
            "Open the configured authenticator application.",
            "Contact IT support if verification continues to fail."
        ]
    }
]
