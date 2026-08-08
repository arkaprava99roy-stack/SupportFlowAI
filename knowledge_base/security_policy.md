---
title: Security & Account Protection Policy
category: SECURITY
version: "2.3"
updated_at: "2026-08-01"
document: security_policy.md
---

# SupportFlow Security & Compromise Protocol

## 1. Compromised Account & Unauthorized Access Protocol
If you suspect someone has unauthorized access to your account or your credentials have been compromised:
- **Immediate Action**: Immediately log in and change your password from the security settings. Terminate all active sessions under **Settings > Security > Active Sessions > Log Out All Devices**.
- If you are locked out or your account email has been altered by an unauthorized actor, immediately contact our dedicated Security Incident Response Desk at `security@supportflow.ai` or notify our AI agent to trigger an emergency security freeze.
- We will immediately freeze your account, invalidate all active OAuth tokens, and initiate identity verification to restore your ownership.

## 2. Fraud Prevention & Suspicious Transactions
- Our automated fraud detection monitors for anomalous login locations, rapid successive failed payment attempts, and sudden shipping address changes on high-value orders.
- Orders flagged as high risk require manual verification before dispatch.
- If you detect an unauthorized purchase on your account, report it within 24 hours so we can intercept fulfillment and immediately issue a full reversal.

## 3. Data Protection, Encryption & Compliance
- SupportFlow uses AES-256 encryption at rest and TLS 1.3 encryption in transit for all sensitive user information and transaction logs.
- We never store raw credit card numbers or CVV codes; all transactions are tokenized via PCI-DSS Level 1 certified processors.

## 4. Reporting Vulnerabilities (Bug Bounty)
- Security researchers who discover vulnerabilities are encouraged to responsibly disclose them through our Responsible Disclosure Program at `security-bounty@supportflow.ai`.
