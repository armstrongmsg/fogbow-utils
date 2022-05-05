from abc import ABCMeta, abstractmethod


class FogbowTest:
    __metaclass__ = ABCMeta

    @abstractmethod
    def test(self):
        pass

    @abstractmethod
    def get_test_name(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass
