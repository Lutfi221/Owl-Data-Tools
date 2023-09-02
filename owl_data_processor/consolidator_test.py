from .consolidator import ConsolidatorDictionary


class TestConsolidatorDictionary:
    def test_1_use_value(self):
        cd = ConsolidatorDictionary()
        assert cd.use_value("aa") == 0
        assert cd.use_value("bb") == 1
        assert cd.use_value("cc") == 2
        assert cd.use_value("cc") == 2
        assert cd.use_value("bb") == 1
        assert cd.use_value("aa") == 0

        cd_values = cd.generate_values_list()
        assert cd_values == ["aa", "bb", "cc"]

    def test_2_empty(self):
        cd = ConsolidatorDictionary()

        cd_values = cd.generate_values_list()
        assert cd_values == []
