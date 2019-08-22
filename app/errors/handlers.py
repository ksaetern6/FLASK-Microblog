from flask import render_template
from app import db
from app.errors import bp

##
# @type: errorhandler
# @name: not_found_error
# @desc: if 404 error then return '404.html' template with secondary value 404
##
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

##
# @type: errorhandler
# @name: internal_error
# @desc: if interal error 500 like a db error then return '500.html' template
#   session.rollback() is invoked to not interfere with db access
##
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
