
from .utilities import display_knowl
from sage.structure.unique_representation import UniqueRepresentation

class TdElt(object):
    def td(self, colspan=1, info=None):
        keys = []
        if colspan != 1:
            keys.append(' colspan=%s' % colspan)
        if self.advanced and (info is None or not info.get('advanced_search')):
            keys.append(' class="advanced"')
        return '<td%s>' % (''.join(keys))

class Spacer(TdElt):
    def __init__(self, colspan=1, advanced=False):
        self.colspan = colspan
        self.advanced = advanced

class BasicSpacer(Spacer):
    def __init__(self, msg, colspan=1, advanced=False):
        Spacer.__init__(self, colspan=colspan, advanced=advanced)
        self.msg = msg

    def html(self, info=None):
        return self.td(self.colspan, info) + self.msg + '</td>'

class CheckboxSpacer(Spacer):
    def __init__(self, checkbox, colspan=1, advanced=False):
        Spacer.__init__(self, colspan=colspan, advanced=advanced)
        self.checkbox = checkbox

    def html(self, info=None):
        return self.td(self.colspan, info) + self.checkbox._label(info) + " " + self.checkbox._input(info) + "</td>"

class SearchBox(TdElt):
    """
    Class abstracting the input boxes used for LMFDB searches.
    """
    def __init__(self, name=None, label=None, knowl=None, colspan=(1,1,1), short_label=None, advanced=False, example_col=False, qfield=None):
        self.name = name
        self.label = label
        self.knowl = knowl
        self.label_colspan, self.input_colspan, self.short_colspan = colspan
        if short_label is None:
            short_label = label
            if label is not None:
                short_label = label.lower()
        self.short_label = short_label
        self.advanced = advanced
        self.example_col = example_col
        self.qfield = name if qfield is None else qfield

    def _label(self, info):
        label = self.label if info is None else self.short_label
        if self.knowl is not None:
            label = display_knowl(self.knowl, label)
        return label

    def label_html(self, info=None):
        colspan = self.label_colspan if info is None else self.short_colspan
        return self.td(colspan, info) + self._label(info) + "</td>"

    def input_html(self, info=None):
        colspan = self.input_colspan if info is None else self.short_colspan
        return self.td(colspan, info) + self._input(info) + '</td>'

    def example_html(self, info=None):
        if self.example_col:
            return '<td></td>'

class TextBox(SearchBox):
    """
    A text box for user input.

    INPUT:

    - ``name`` -- the name of the input (will show up in URL)
    - ``label`` -- the label for the input, shown on browse page
    - ``knowl`` -- a knowl id to apply to the label (you can set as None include a display_knowl directly in the label/short_label if the whole text shouldn't be a knowl link)
    - ``example`` -- the example in the input box
    - ``example_span`` -- the formexample span (defaults to example)
    - ``width`` -- the width of the input element on the browse page
    - ``short_width`` -- the width of the input element on the refine-search page
    - ``short_label`` -- the label on the refine-search page, if different
    - ``qfield`` -- the corresponding database column (defaults to name).  Not currently used.
    """
    def __init__(self, name=None, label=None, knowl=None, example=None, example_span=None, colspan=(1,1,1), width=15, short_width=10, short_label=None, advanced=False, example_col=None, qfield=None):
        self.example = example
        self.example_span = example if example_span is None else example_span
        if example_col is None:
            example_col = bool(self.example_span)
        SearchBox.__init__(self, name, label, knowl=knowl, colspan=colspan, short_label=short_label, advanced=advanced, example_col=example_col, qfield=qfield)
        self.width = width
        self.short_width = short_width

    def _input(self, info):
        keys = ['type="text"', 'name="%s"' % self.name]
        if self.example is not None:
            keys.append('example="%s"' % self.example)
        if info is None:
            if self.width is not None:
                keys.append('size=%s' % self.width)
        else:
            if self.short_width is not None:
                keys.append('size=%s' % self.short_width)
            if self.name in info:
                keys.append('value="%s"' % info[self.name])
        return '<input type="text" ' + " ".join(keys) + '/>'

    def example_html(self, info=None):
        if self.example_col:
            return self.td(info=info) + '<span class="formexample">e.g. %s</span></td>' % self.example_span

class SelectBox(SearchBox):
    def __init__(self, name=None, label=None, options=[], knowl=None, colspan=(1,1,1), width=107, short_width=105, short_label=None, advanced=False, example_col=False, qfield=None):
        SearchBox.__init__(self, name, label, knowl=knowl, colspan=colspan, short_label=short_label, advanced=advanced, example_col=example_col, qfield=qfield)
        self.options = options
        self.width = width
        self.short_width = short_width
        self.example_col = example_col

    def _input(self, info):
        keys = ['name="%s"' % self.name]
        if info is None:
            if self.width is not None:
                keys.append('style="width: %spx"' % self.width)
        else:
            if self.short_width is not None:
                keys.append('style="width: %spx"' % self.short_width)
        opts = []
        for value, display in self.options:
            if info is None and value == '' or info is not None and info.get(self.name, '') == value:
                selected = ' selected'
            else:
                selected = ''
            if value is None:
                value = ''
            else:
                value = 'value="%s"' % value
            opts.append('<option %s%s>%s</option>' % (value, selected, display))
        return '        <select %s>\n%s\n        </select>' % (' '.join(keys), ''.join('\n' + ' '*10 + opt for opt in opts))

class CheckBox(SearchBox):
    def _input(self, info=None):
        return '<input type="checkbox" name="%s">' % self.name

class SkipBox(TextBox):
    def _input(self, info=None):
        return ''

    def _label(self, info=None):
        return ''

class TextBoxWithSelect(TextBox):
    def __init__(self, name, label, select_box, split=True, **kwds):
        self.select_box = select_box
        TextBox.__init__(self, name, label, **kwds)

    def label_html(self, info=None):
        colspan = self.label_colspan if info is None else self.short_colspan
        return self.td(colspan, info) + self._label(info) + '<div class="float-right">' + self.select_box._input(info) + "</div></td>"

class SearchArray(UniqueRepresentation):
    def __init__(self, browse_array, refine_array):
        self.browse_array = browse_array
        self.refine_array = refine_array
        self.all_search = []
        for array in [browse_array, refine_array]:
            for row in array:
                if isinstance(row, (list, tuple)):
                    for col in row:
                        if isinstance(col, SearchBox) and col not in self.all_search:
                            self.all_search.append(col)

    def html(self, info=None):
        if info is None:
            # browse page
            lines = []
            for row in self.browse_array:
                if isinstance(row, Spacer):
                    lines.append('\n      ' + row.html())
                else:
                    cols = []
                    for box in row:
                        cols.append(box.label_html())
                        cols.append(box.input_html())
                        ex = box.example_html()
                        if ex:
                            cols.append(ex)
                    lines.append(''.join('\n      ' + col for col in cols))
        else:
            # refine search page
            lines = []
            for row in self.refine_array:
                if isinstance(row, Spacer):
                    lines.append(row.html(info))
                else:
                    labels = []
                    inputs = []
                    for box in row:
                        labels.append(box.label_html(info))
                        inputs.append(box.input_html(info))
                    lines.append(''.join('\n      ' + label for label in labels))
                    lines.append(''.join('\n      ' + inp for inp in inputs))
        return '  <table border="0">' + ''.join('\n    <tr>' + line + '\n    </tr>' for line in lines) + '\n  </table>'
