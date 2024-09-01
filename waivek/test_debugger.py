import unittest
from unittest.mock import Mock, patch, create_autospec
from types import FrameType, CodeType, TracebackType
from typing import List
import pdb
from json.decoder import JSONDecodeError
# Import the functions you want to test
from waivek.error2 import (
    select_frame_for_file,
    _select_frame_silent,
    do_down_silent,
    do_up_silent,
    handler,
)

def create_mock_frame(filename: str) -> FrameType:
    mock_code = create_autospec(CodeType, spec_set=True)
    mock_code.co_filename = filename
    mock_frame = create_autospec(FrameType, spec_set=True)
    mock_frame.f_code = mock_code
    return mock_frame

class TestDebugger(unittest.TestCase):
    def test_select_frame_for_file(self):
        mock_frames: List[FrameType] = [
            create_mock_frame("file1.py"),
            create_mock_frame("file2.py"),
            create_mock_frame("file3.py"),
        ]
        result = select_frame_for_file(mock_frames, "file2.py")
        self.assertEqual(result, mock_frames[1], "Should select the correct frame")
        result = select_frame_for_file(mock_frames, "nonexistent.py")
        self.assertIsNone(result, "Should return None for non-existent file")

    def test_select_frame_silent(self):
        mock_pdb = Mock(spec=pdb.Pdb)
        mock_pdb.stack = [(create_mock_frame(f"file{i}.py"), i) for i in range(3)]
        _select_frame_silent(mock_pdb, 1)
        self.assertEqual(mock_pdb.curindex, 1, "Should set correct curindex")
        self.assertEqual(mock_pdb.curframe, mock_pdb.stack[1][0], "Should set correct curframe")
        self.assertEqual(mock_pdb.curframe_locals, mock_pdb.curframe.f_locals, "Should set correct curframe_locals")
        self.assertIsNone(mock_pdb.lineno, "Should set lineno to None")

    def test_do_down_silent(self):
        mock_pdb = Mock(spec=pdb.Pdb)
        mock_pdb.stack = [(create_mock_frame(f"file{i}.py"), i) for i in range(3)]
        mock_pdb.curindex = 0
        do_down_silent(mock_pdb, 1)
        self.assertEqual(mock_pdb.curindex, 1, "Should move down one frame")

    def test_do_up_silent(self):
        mock_error = Mock(spec=Exception)
        mock_pdb = Mock(spec=pdb.Pdb)
        mock_pdb.stack = [(create_mock_frame(f"file{i}.py"), i) for i in range(3)]
        mock_pdb.curindex = 2
        do_up_silent(mock_pdb, mock_error, 1)
        self.assertEqual(mock_pdb.curindex, 1, "Should move up one frame")

    @patch('pdb.Pdb')
    @patch('traceback.walk_tb')
    def test_handler(self, mock_walk_tb, mock_pdb_class):
        mock_pdb = Mock(spec=pdb.Pdb)
        mock_pdb_class.return_value = mock_pdb
        mock_error = JSONDecodeError('Expecting value', '', 0)
        mock_error.__traceback__ = create_autospec(TracebackType, spec_set=True)
        mock_walk_tb.return_value = [
            (create_mock_frame("file1.py"), None),
            (create_mock_frame(__file__), None),
        ]
        with patch('builtins.__import__', side_effect=mock_error):
            with handler():
                __import__('json')  # This will raise the JSONDecodeError
        mock_pdb.reset.assert_called_once()
        mock_pdb.setup.assert_called_once()
        self.assertTrue(hasattr(mock_pdb, 'do_x'), "Should add custom 'x' command")
        self.assertTrue(hasattr(mock_pdb, 'do_y'), "Should add custom 'y' command")
        self.assertTrue(hasattr(mock_pdb, 'do_z'), "Should add custom 'z' command")
        mock_pdb._cmdloop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
