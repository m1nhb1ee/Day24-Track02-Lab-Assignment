# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam (production policy: region VN only)
- [x] Backup cũng phải ở trong lãnh thổ VN (backup bucket/volume pinned to VN region)
- [x] Log việc transfer data ra ngoài nếu có (audit log + deny rule tại OPA cho restricted data)

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training (consent flag required trước ETL)
- [x] Có mechanism để user rút consent (Right to Erasure) (revoke API + deletion workflow)
- [x] Lưu consent record với timestamp (consent table có created_at/updated_at)

## C. Breach Notification (72h)
- [x] Có incident response plan (severity matrix + on-call escalation)
- [x] Alert tự động khi phát hiện breach (Prometheus alert rule + pager/email)
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h (SOP + legal owner)

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 envelope encryption for sensitive fields; TLS 1.3 for transport | ✅ Done | Infra Team |
| Audit logging | API access logging + security scan reports under `reports/` | ✅ Done | Platform Team |
| Breach detection | Prometheus/Grafana monitoring + incident alert workflow | ✅ Done | Security Team |

## F. Technical notes completed
- Raw patient data chỉ cho admin truy cập qua RBAC endpoint `/api/patients/raw`.
- ML engineer dùng endpoint anonymized/training data, không đọc raw PII.
- OPA deny rule chặn export dữ liệu restricted ra ngoài VN.
- Security pre-commit hook: git-secrets + bandit + pip-audit để chặn secret/vulnerability trước commit.
