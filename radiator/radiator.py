import json
from flask import Flask, render_template, request
from models import JenkinsCI

app = Flask(__name__)
app.config.from_object('settings')

@app.route('/')
def index():
    view = request.args.get('view', '')
    return render_template('index.html', view=view)

@app.route('/builds')
def builds():
    """
        Return the json data of jenkins server
    """

    url = app.config['JENKINS_URL']
    view = request.args.get('view') or app.config['JENKINS_DEFAULT_URL']
    timeout = app.config['JENKINS_TIMEOUT']

    jenkins = JenkinsCI(url=url, view=view, timeout=timeout)

    jobs = None
    result = None

    try:
        jobs = jenkins.get_all_jobs()
    except Exception, error:
        result = {'status': 'error', 'content': str(error.reason)}

    if not result:
        html = ''
        for job in jobs:
            blame = job['blame']
            if job['status'][0] in ('failed', 'unstable'):
                blame = "<br /><span class='blame'>%s</span>" % job['blame']

            html += "<li class = 'job " + " ".join(job['status']) + \
                    "'>%s%s</li>" % (job['name'], blame)

            result = {'status': 'ok', 'content': html}

    return json.dumps(result)

if __name__ == '__main__':
    app.run(debug=True)
