class Element:
    def __init__(self, tag, inner_html=""):
        self.tag = tag
        self.attrs = {}
        self.inner_html = inner_html

    def __str__(self):
        s  = "<"
        s += self.tag
        for attr, value in self.attrs.items():
            s += " "
            s += attr
            s += "="
            s += '"'
            s += value
            s += '"'
        s += ">"
        s += self.inner_html
        s += "</"
        s += self.tag
        s += ">"
        return s

    def set(self, attr, value):
        self.attrs[attr] = value
        return self

    def delete(self, attr):
        del self.attrs[attr]
        return self

    def inner(self, inner_html):
        self.inner_html = inner_html
        return self
