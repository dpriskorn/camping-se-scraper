from main import Site, CampingList


class TestSite:
    def test_generate_url(self):
        site = Site(drupal_id="123", name="Test Camp", lat=56.5, long=12.3)
        site.generate_url()
        assert site.website == "https://camping.se/node/123"

    def test_model_dump_excludes_lat_long(self):
        site = Site(drupal_id="123", name="Test Camp", lat=56.5, long=12.3)
        dump = site.model_dump(exclude={"lat", "long"})
        assert "lat" not in dump
        assert "long" not in dump
        assert dump["drupal_id"] == "123"
        assert dump["name"] == "Test Camp"

    def test_site_with_defaults(self):
        site = Site(drupal_id="456", name="Minimal Camp", lat=1.0, long=2.0)
        assert site.website == ""

    def test_site_model_dump(self):
        site = Site(drupal_id="789", name="Dump Test", lat=10.0, long=20.0, website="https://test.com")
        dump = site.model_dump()
        assert dump["drupal_id"] == "789"
        assert dump["name"] == "Dump Test"
        assert dump["lat"] == 10.0
        assert dump["long"] == 20.0
        assert dump["website"] == "https://test.com"


class TestCampingList:
    def test_camping_list_init(self):
        camping_list = CampingList()
        assert camping_list.sites == []
        assert camping_list.items == []
        assert "User-Agent" in camping_list.headers

    def test_headers_contains_expected_keys(self):
        camping_list = CampingList()
        expected_keys = ['User-Agent', 'Accept', 'Accept-Language', 'X-Requested-With',
                        'DNT', 'Connection', 'Referer', 'Sec-Fetch-Dest', 'Sec-Fetch-Mode',
                        'Sec-Fetch-Site']
        for key in expected_keys:
            assert key in camping_list.headers

    def test_camping_list_headers_user_agent(self):
        camping_list = CampingList()
        assert camping_list.headers['User-Agent'] == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'

    def test_camping_list_sites_append(self):
        camping_list = CampingList()
        site = Site(drupal_id="999", name="Append Test", lat=5.0, long=6.0)
        camping_list.sites.append(site)
        assert len(camping_list.sites) == 1
        assert camping_list.sites[0].drupal_id == "999"


class TestExportToGeoJson:
    def test_export_to_geojson_creates_file(self, tmp_path):
        camping_list = CampingList()
        site1 = Site(drupal_id="1", name="Site One", lat=56.5, long=12.3)
        site2 = Site(drupal_id="2", name="Site Two", lat=57.6, long=13.4)
        camping_list.sites.append(site1)
        camping_list.sites.append(site2)

        test_file = tmp_path / "test_output.geojson"
        camping_list.export_to_geojson(str(test_file))

        assert test_file.exists()
        content = test_file.read_text()
        assert "Site One" in content
        assert "Site Two" in content
        assert "https://camping.se/node/1" in content
        assert "https://camping.se/node/2" in content

    def test_export_to_geojson_with_no_sites(self, tmp_path):
        camping_list = CampingList()
        test_file = tmp_path / "empty_output.geojson"
        camping_list.export_to_geojson(str(test_file))

        assert test_file.exists()
        content = test_file.read_text()
        assert "FeatureCollection" in content
