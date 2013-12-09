import os
import datetime
import sys
from py.xml import html
from py.xml import raw
import pkg_resources
from manifestparser import ManifestParser


def generate_html(manifest):

    test_logs = []

    def table_row(test):
        status = 'Pass'

        status_class = ' passed'

        cls_name = os.path.basename(test['here'])
        tc_name = test['name']
        travis = 'Running'
        travis_class = ' passed'

        emulator = 'Running'
        emulator_class = ' passed'

        hamachi = 'Running'
        hamachi_class = ' passed'

        tbpl = 'Not Running'
        tbpl_class = ' error'


        # skip if mark
        if 'skip-if' in test.keys():
            if 'device == "desktop"' in test['skip-if']:
                travis = 'Not running'
                travis_class = ' error'
            elif 'device == "qemu"' in test['skip-if']:
               emulator = 'Not running'
               emulator_class = ' error'

        # tbpl-disabled
        if 'tbpl' in test.keys():
            if test['tbpl-disabled']:
                tbpl = 'Disabled ' + test['tbpl-disabled']
                tbpl_class = ' skipped'
            else:
                tbpl = 'Running'
                tbpl_class = ' passed'

        # fail if mark
        if 'fail-if' in test.keys():
            if 'device == "desktop"' in test['fail-if']:
                travis = 'Failed'
                travis_class = ' skipped'
            elif 'device == "qemu"' in test['fail-if']:
                emulator = 'Failed'
                emulator_class = ' skipped'
            elif 'device == "msm7627a"' in test['fail-if']:
                hamachi = 'Failed'
                hamachi_class = ' skipped'

        if 'expected' in test.keys():
            status = 'Fail'
            status_class = ' skipped'

        if 'disabled' in test.keys():
            status = 'Not running'
            status_class = ' failure'

        test_logs.append(html.tr([
                                     html.td(status, class_ = 'col-status' + status_class),
                                     html.td(cls_name, class_ = 'col-class'),
                                     html.td(tc_name, class_ = 'col-name'),
                                     html.td(hamachi, class_ = 'col-hamachi' + hamachi_class),
                                     html.td(travis, class_ = 'col-travis' + travis_class),
                                     html.td(emulator, class_ = 'col-emulator' + emulator_class),
                                     html.td(tbpl, class_ = 'col-tbpl' + tbpl_class)
                                     ],
                                 class_ = 'results-table-row'))

    # generate table entry's
    for test in manifest.tests:
        table_row(test)

    # main HTML file
    doc = html.html(
        html.head(
            html.meta(charset = 'utf-8'),
            html.title('Test Report'),
            html.style(raw(pkg_resources.resource_string(
                __name__, os.path.sep.join(['resources', 'report', 'style.css']))),
                       type = 'text/css')),
        html.body(
            html.script(raw(pkg_resources.resource_string(
                __name__, os.path.sep.join(['resources', 'report', 'jquery.js']))),
                        type = 'text/javascript'),
            html.script(raw(pkg_resources.resource_string(
                __name__, os.path.sep.join(['resources', 'report', 'main.js']))),
                        type = 'text/javascript'),
            html.h2('Tests'),
            html.table([html.thead(
                html.tr([
                    html.th('Expected to:', class_ = 'sortable', col = 'status'),
                    html.th('Class', class_ = 'sortable', col = 'class'),
                    html.th('Test Name', class_ = 'sortable', col = 'name'),
                    html.th('Hamachi', class_ = 'sortable',  col = 'hamachi'),
                    html.th('Travis', class_ = 'sortable',  col = 'travis'),
                    html.th('Emulator', class_ = 'sortable',  col = 'emulator'),
                    html.th('TBPL', class_ = 'sortable', col = 'tbpl'),
                        ]), id = 'results-table-head'),
                        html.tbody(test_logs, id = 'results-table-body')], id = 'results-table')))

    return doc.unicode()

# change default encoding to avoid encoding problem for page source
reload(sys)
sys.setdefaultencoding('utf-8')

here = os.path.dirname(os.path.abspath(__file__))

# read manifest
manifest_path = os.path.join(here, 'tests/manifest.ini')
manifest = ManifestParser(manifests = (manifest_path,))

#read tbpl
tbpl_path = os.path.join(here, 'tests/tbpl-manifest.ini')
tbpl = ManifestParser(manifests = (tbpl_path,))


# merge main manifest with TBPL
# TODO: add tests in TBPL and not in manifest
for test in tbpl.tests:
    for i, te in enumerate(manifest.tests):
        if te['path'] == test['path']:
            manifest.tests[i]['tbpl'] = True
            if 'disabled' in test.keys():
                manifest.tests[i]['tbpl-disabled'] = test['disabled']
            else:
                manifest.tests[i]['tbpl-disabled'] = False

# Generate HTML file
file = os.path.join(here, 'out.html')
with open(file, 'w') as f:
    f.write(generate_html(manifest))