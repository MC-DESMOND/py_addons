import json
import os
import tempfile

class JSONDict:
    """
    Dictionary-like object that persists its data to a JSON file.
    Automatically flushes changes to disk.
    """

    def __init__(self, filepath):
        self.original_path = filepath
        self.filepath = filepath
        self._data = {}

        try:
            # Load existing data if file exists, else create new file
            if os.path.exists(filepath):
                self._data = self._read_file(filepath)
            else:
                self._write_file(filepath, self._data)
        except PermissionError:
            # Switch to temp file if permission denied
            self._switch_to_temp_file()

    def _switch_to_temp_file(self):
        # Raise error if permission denied (temp file logic commented out)
        raise PermissionError(f"Permission denied for '{self.original_path}'")
        # Uncomment below to use temp file instead of raising error
        # temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w+', encoding='utf-8')
        # json.dump(self._data, temp)
        # temp.close()
        # self.filepath = temp.name

    def _read_file(self, path):
        # Read JSON file and return dict
        with open(path, 'r') as f:
            return json.load(f)

    def _write_file(self, path, data):
        # Write dict to JSON file
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def flush(self):
        """Write the internal dict to the file."""
        try:
            self._write_file(self.filepath, self._data)
        except PermissionError:
            self._switch_to_temp_file()
            self._write_file(self.filepath, self._data)

    # Dict-like methods
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self.flush()

    def __delitem__(self, key):
        del self._data[key]
        self.flush()

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __repr__(self):
        return repr(self._data)

    def clear(self):
        self._data.clear()
        self.flush()

from bson import BSON, decode_all

class BSONDict:
    """
    Dictionary-like object that persists its data to a BSON file.
    Automatically flushes changes to disk.
    """

    def __init__(self, filepath):
        self.original_path = filepath
        self.filepath = filepath
        self._data = {}

        try:
            # Load existing data if file exists, else create new file
            if os.path.exists(filepath):
                self._data = self._read_file(filepath)
            else:
                self._write_file(filepath, self._data)
        except PermissionError:
            # Switch to temp file if permission denied
            self._switch_to_temp_file()

    def _switch_to_temp_file(self):
        # Raise error if permission denied (temp file logic commented out)
        raise PermissionError(f"Permission denied for '{self.original_path}'")
        # Uncomment below to use temp file instead of raising error
        # temp = tempfile.NamedTemporaryFile(delete=False, suffix=".bson", mode='wb')
        # temp.write(BSON.encode(self._data))
        # temp.close()
        # self.filepath = temp.name

    def _read_file(self, path):
        # Read BSON file and return dict
        with open(path, 'rb') as f:
            content = f.read()
            return decode_all(content)[0] if content else {}

    def _write_file(self, path, data):
        # Write dict to BSON file
        with open(path, 'wb') as f:
            f.write(BSON.encode(data))

    def flush(self):
        """Write the internal dict to the BSON file."""
        try:
            self._write_file(self.filepath, self._data)
        except PermissionError:
            self._switch_to_temp_file()
            self._write_file(self.filepath, self._data)

    # Dict-like methods
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self.flush()

    def __delitem__(self, key):
        del self._data[key]
        self.flush()

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __repr__(self):
        return repr(self._data)

    def clear(self):
        self._data.clear()
        self.flush()
