def test_supervised_dataset_audit_module_imports():
    import scripts.audit_supervised_dataset as audit

    assert callable(audit.main)
