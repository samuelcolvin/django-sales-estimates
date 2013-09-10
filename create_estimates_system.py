import subprocess, os, shutil, sys, re
def clone(dest_dir):
    url = 'https://github.com/samuelcolvin/django-sales-estimates.git'
    do_clone = False
    try:
        os.mkdir(dest_dir)
    except OSError, e:
        if e.errno == 17:
            response = raw_input('Directory "%s" already exists, would you like to replace it? [y/n] ' % dest_dir)
            if response.lower() == 'y':
                shutil.rmtree(dest_dir)
                os.mkdir(dest_dir)
            else:
                print 'not cloning, assiming "%s" already contains a Sales Estimates system' % dest_dir
                return True
        else:
            print e
            return False
    print 'Cloning Sales Estimates'
    response = subprocess.call(['git', 'clone', '--recursive', url, dest_dir])
    if response == 0:
        print '---------------\nSuccessfully clone repo\n'
        return True
    else:
        return False

def setup_settings(project_name):
    settings_fname = '%s/settings.py' % project_name
    text = open(settings_fname, 'r').read()
    text = re.sub(r"(SITE_TITLE = )'.*'", r"\1'%s'" % project_name, text)
    db_finds=list(re.finditer(r'DATABASES *=',text))
    open(settings_fname, 'w').write(text)
    print '---------------\nProject name changed in %s\n' % settings_fname
    if len(db_finds) != 2:
        print 'unable to find DATABASE info, not setting database'
        return
    print 'Setting DATABASE settings in %s:' % settings_fname
    db_name = raw_input('Enter db name: ')
    if db_name == '':
        print 'db name blank, not setting database'
        return
    db_username = raw_input('Enter db username: ')
    if db_username == '':
        print 'db username blank, not setting database'
        return
    db_password = raw_input('Enter db password: ')
    if db_password == '':
        print 'db password blank, not setting database'
        return
    db_settings = (('NAME', db_name), ('USER', db_username), ('PASSWORD', db_password))
    db_settings_string = text[db_finds[0].start():db_finds[1].start()]
    for field_name, setting in db_settings:
        db_settings_string = re.sub(r"('%s':).*," % field_name, r"\1 '%s'," % setting, db_settings_string)
    text = text[:db_finds[0].start()] + db_settings_string + text[db_finds[1].start():]
    open(settings_fname, 'w').write(text)
    

def collectstatic(project_name):
    manage = '%s/manage.py' % project_name
    print 'collecting static files with %s:' % manage
    response = subprocess.call(['python', manage, 'collectstatic'])
    if response == 0:
        print '---------------\nSuccessfully collected static files.'
    else:
        return False
    print 'running syncdb with %s:' % manage
    response = subprocess.call(['python', manage, 'syncdb'])
    if response == 0:
        print '---------------\nSuccessfully sync\'d db.'
        return True
    else:
        return False
    
    
if __name__ == '__main__':
    project_name = raw_input('Enter the new project name (numbers and letters only): ')
    print 'New project name: "%s"' % project_name
    if not clone(project_name):
        print 'ERROR cloning repo, exitting'
        sys.exit(2)
        
    setup_settings(project_name)

    if not collectstatic(project_name):
        print 'ERROR collecting statics or syncing, exitting'
        sys.exit(2)
    print 'Sales Estimates cloned to %s. You now need to' + \
        ' set the server to point at this django instance and run it.'
