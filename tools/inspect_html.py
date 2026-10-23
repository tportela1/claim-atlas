"""Inspect generated HTML without executing it or exposing report content."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

DESTINATIONS = {'next-steps','discoveries','verification','tracking','payments','watchlist','closed','safety','coverage','top','main'}

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set(); self.references = []; self.errors = []; self.csp = False
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in {'script','iframe','object','embed','form','input','button','link','base'}:
            self.errors.append('Unexpected active or external-resource element')
        if any(name.lower().startswith('on') for name in attrs):
            self.errors.append('Inline event handler')
        if tag == 'meta' and attrs.get('http-equiv','').lower() == 'content-security-policy':
            value = attrs.get('content','')
            self.csp = all(rule in value for rule in ["default-src 'none'", "base-uri 'none'", "form-action 'none'"])
        if 'id' in attrs:
            if attrs['id'] in self.ids: self.errors.append('Duplicate destination')
            self.ids.add(attrs['id'])
        if tag == 'a':
            url = attrs.get('href','')
            if url.startswith('#'): self.references.append(url[1:])
            else:
                try:
                    parsed = urlsplit(url)
                    valid = parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password and not any(ord(c)<33 for c in url)
                except ValueError: valid = False
                if not valid: self.errors.append('Unsafe external reference')
                if not {'noopener','noreferrer'} <= set(attrs.get('rel','').split()): self.errors.append('External reference lacks isolation')
        if tag == 'img' and not attrs.get('src','').startswith('data:'):
            self.errors.append('External image')
    handle_startendtag = handle_starttag

def audit(path):
    parser = Inspector(); parser.feed(Path(path).read_text(encoding='utf-8'))
    if not parser.csp: parser.errors.append('Missing restrictive content policy')
    if not DESTINATIONS <= parser.ids: parser.errors.append('Missing workspace destination')
    if not set(parser.references) <= parser.ids: parser.errors.append('Broken internal reference')
    return sorted(set(parser.errors))
