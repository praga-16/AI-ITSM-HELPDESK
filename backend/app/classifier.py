def classify(text):
    t = text.lower()

    if "vpn" in t:
        return {
            "intent":"Incident","category":"Network","subcategory":"VPN",
            "priority":"P2","impact":"Individual","urgency":"High",
            "assignment_group":"Network Support","summary":"VPN authentication failure",
            "suggested_resolution":"VPN troubleshooting","confidence":0.96,
            "route":"incident"
        }

    if any(x in t for x in ["password expired","password has expired","password reset","forgot password"]):
        return {
            "intent":"Automatable Issue","category":"Account","subcategory":"Password",
            "priority":"P2","impact":"Individual","urgency":"High",
            "assignment_group":"Service Desk","summary":"Password reset request",
            "suggested_resolution":"Reset password and validate authentication",
            "confidence":0.97,"route":"self_heal"
        }

    if any(x in t for x in ["visual studio code","vscode","vs code"]):
        return {
            "intent":"Service Request","category":"Software","subcategory":"Software Installation",
            "priority":"P3","impact":"Individual","urgency":"Medium",
            "assignment_group":"Software Support","summary":"Visual Studio Code installation request",
            "suggested_resolution":"Create software provisioning request",
            "confidence":0.97,"route":"software"
        }

    if any(x in t for x in ["outlook","synchronization","synchronisation","wifi","wi-fi","laptop performance","application access"]):
        return {
            "intent":"Knowledge Question","category":"IT Support","subcategory":"General Troubleshooting",
            "priority":"P3","impact":"Individual","urgency":"Medium",
            "assignment_group":"Service Desk","summary":"IT support knowledge question",
            "suggested_resolution":"Search approved knowledge base",
            "confidence":0.90,"route":"knowledge"
        }

    return {
        "intent":"Unknown","category":"Unclassified","subcategory":"Unknown",
        "priority":"P3","impact":"Individual","urgency":"Medium",
        "assignment_group":"Service Desk","summary":"Unsupported helpdesk question",
        "suggested_resolution":"Escalate to helpdesk","confidence":0.32,
        "route":"escalate"
    }
