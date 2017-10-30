import prove.remote


class DummyClass: pass


def test_serialize_unserialize():
	obj = DummyClass()
	obj.foo = 'bar'
	serialized = prove.remote.serialize(obj)
	unserialized = prove.remote.unserialize(serialized)
	assert isinstance(unserialized, DummyClass)
	assert unserialized.foo == 'bar'


def test_encode_decode():
	data = {'foo': 'bar'}
	encoded = prove.remote.encode(data)
	decoded = prove.remote.decode(encoded)
	assert decoded == data
