from .dictionary import Dictionary, DictionaryMapper


class TestConsolidatorDictionary:
    def test_use_value(self):
        cd = Dictionary()
        assert cd.use_value("aa") == 0
        assert cd.use_value("bb") == 1
        assert cd.use_value("cc") == 2
        assert cd.use_value("cc") == 2
        assert cd.use_value("bb") == 1
        assert cd.use_value("aa") == 0

        cd_values = cd.generate_values_list()
        assert cd_values == ["aa", "bb", "cc"]

    def test_empty(self):
        cd = Dictionary()

        cd_values = cd.generate_values_list()
        assert cd_values == []


class TestDictionaryMapper:
    def test_source_to_target(self):
        source_list = ["f", "g", "h", "a", "c"]

        target = Dictionary()
        target.use_value("a")
        target.use_value("b")
        target.use_value("c")
        target.use_value("d")
        target.use_value("e")

        mapper = DictionaryMapper(source_list, target)

        # Do it twice
        for i in range(0, 2):
            assert mapper.source_to_target(0) == 5
            assert mapper.source_to_target(1) == 6
            assert mapper.source_to_target(2) == 7
            assert mapper.source_to_target(3) == 0
            assert mapper.source_to_target(4) == 2
