from bjj import bjj


def test_fileiterator(tmpdir):
    xml = tmpdir.join('file.xml')
    xml.write('<some>xml</some>')

    fi = bjj.FileIterator(str(xml))

    assert isinstance(fi, bjj.FileIterator)
    assert len(fi) == 1

    count = 0
    for name, content in fi:
        count += 1
        assert name == str(xml)
        assert isinstance(content, dict)
        assert content == {'some': 'xml'}

    assert count == len(fi)
