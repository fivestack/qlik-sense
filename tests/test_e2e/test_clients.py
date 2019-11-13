from tests.test_e2e import config

qs_ssl = config.qs_ssl
qs_ssl_restricted = config.qs_ssl_restricted
qs_ntlm = config.qs_ntlm
qs_sspi = config.qs_sspi


class TestClient:

    def test_ssl_restricted(self):
        ssl_count = qs_ssl.stream.query_count()
        ssl_restricted_count = qs_ssl_restricted.stream.query_count()
        assert 0 < ssl_restricted_count <= ssl_count

    def test_ntlm(self):
        ssl_count = qs_ssl.stream.query_count()
        ntlm_count = qs_ntlm.stream.query_count()
        assert 0 < ntlm_count <= ssl_count

    def test_sspi(self):
        ssl_count = qs_ssl.stream.query_count()
        sspi_count = qs_sspi.stream.query_count()
        assert 0 < sspi_count <= ssl_count

    def test_equivalent_counts(self):
        ssl_restricted_count = qs_ssl_restricted.stream.query_count()
        ntlm_count = qs_ntlm.stream.query_count()
        sspi_count = qs_sspi.stream.query_count()
        assert ssl_restricted_count == ntlm_count == sspi_count
