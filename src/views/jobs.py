import math

from flask import request, session, render_template
from pymongo import DESCENDING


def init_view(app, settings):
    @app.route('/jobs', methods=['GET'])
    def jobs():
        page = int(request.args.get('page', 1))
        limit = 10
        skip = int(page - 1) * limit

        cur = app.db.job_executions.find({}).sort("_id", DESCENDING)

        total_count = cur.count()
        cur.skip(skip)
        cur.limit(limit)
        items = list(cur)
        page_count = math.ceil(total_count / 10)

        user = session['user']
        asset_service_url = settings['asset_service']
        user_profile_image = user.get('profile_image')
        if user_profile_image:
            user_profile_image = user_profile_image.get('_id', None)

        return render_template('jobs.html', user=user, items=items, asset_service_url=asset_service_url,
                               user_profile_image=user_profile_image, page=page, page_count=page_count)