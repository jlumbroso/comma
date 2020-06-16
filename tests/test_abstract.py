
import pytest

import comma.abstract
import comma.exceptions


class TestCloneableCollection:

    SOME_LIST = [0, 2, 1]
    SOME_OTHER_LIST = [2, 3]
    SOME_STRING = "aaaa"
    SOME_OTHER_STRING = "bbbb"

    @staticmethod
    def make_mock_obj(data=None, no_data=False):
        """
        Returns a pseudo class of subtype `comma.abstract.CloneableCollection`
        for testing purposes. Allows customization of the `data` attribute, and
        even deletion of the attribute, if `no_data` is set to `True`.
        """

        # dummy class
        class MockCloneableCollection(comma.abstract.CloneableCollection):
            pass

        # create object
        obj = MockCloneableCollection()

        # configure data
        if no_data:
            assert "data" not in obj.__dict__
        else:
            obj.data = data

        return obj

    def test_no_data(self):
        """

        """
        with pytest.raises(Exception) as exc:
            obj = TestCloneableCollection.make_mock_obj(no_data=True)
            assert "data" not in obj.__dict__
            obj.clone(newdata=self.SOME_LIST)
        assert exc.type is Exception

    def test_not_newdata(self):
        """

        """
        with pytest.raises(ValueError) as exc:
            TestCloneableCollection.make_mock_obj().clone(data=self.SOME_LIST)
        assert exc.type is ValueError

    def test_newdata_none(self):
        """

        """
        with pytest.raises(ValueError) as exc:
            TestCloneableCollection.make_mock_obj().clone(newdata=None)
        assert exc.type is ValueError

    def test_success(self):
        """

        """
        obj1 = TestCloneableCollection.make_mock_obj(data=self.SOME_LIST)
        obj2 = obj1.clone(newdata=self.SOME_OTHER_LIST)

        # check correctness of operation
        assert obj1.data == self.SOME_LIST
        assert obj2.data == self.SOME_OTHER_LIST

    def test_other_kwarg_not_present(self):
        """

        """
        obj1 = TestCloneableCollection.make_mock_obj(data=self.SOME_LIST)
        obj2 = obj1.clone(newdata=self.SOME_OTHER_LIST,
                          other_kwarg=self.SOME_STRING)

        assert obj1.data == self.SOME_LIST
        assert obj2.data == self.SOME_OTHER_LIST
        assert "other_kwarg" not in obj1.__dict__
        assert "other_kwarg" not in obj2.__dict__

    def test_other_kwarg_present(self):
        """

        """
        # NOTE: this test helped locate a bug in the `clone()` method logic
        # where the overwritten kwargs were in fact always overwritten by the
        # original values! yay tests! yay pytest! :-)

        obj1 = TestCloneableCollection.make_mock_obj(data=self.SOME_LIST)

        # create an extra attribute
        obj1.other_kwarg = self.SOME_STRING

        obj2 = obj1.clone(newdata=self.SOME_OTHER_LIST,
                          other_kwarg=self.SOME_OTHER_STRING)

        assert obj1.data == self.SOME_LIST
        assert obj2.data == self.SOME_OTHER_LIST
        assert "other_kwarg" in obj1.__dict__
        assert "other_kwarg" in obj2.__dict__
        assert obj1.other_kwarg == self.SOME_STRING
        assert obj2.other_kwarg == self.SOME_OTHER_STRING

