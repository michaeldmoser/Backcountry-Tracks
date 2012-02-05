import riak

c = riak.RiakClient()
b = c.bucket('comments')
o = b.new('asdf', {'asdf': 'asdf'})

m = o.get_metadata()
m['usermeta'].update({'object_type': 'comment'})
o.set_metadata(m)

o.store()
mapreduce = c.add('comments')
jscript = '''
function (value, keyData, arg) {
    var usermeta = value.values[0].metadata['X-Riak-Meta'];
    if (usermeta['X-Riak-Meta-object_type'] == 'comment') {
        var data = Riak.mapValuesJson(value)[0];
        return [data];
    }

    return [];
}
'''
mapreduce.map(jscript)

objects = mapreduce.run()
print objects


