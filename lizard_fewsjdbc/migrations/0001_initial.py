# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'JdbcSource'
        db.create_table('lizard_fewsjdbc_jdbcsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('jdbc_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('jdbc_tag_name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('connector_string', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('usecustomfilter', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('customfilter', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['JdbcSource'])


    def backwards(self, orm):
        
        # Deleting model 'JdbcSource'
        db.delete_table('lizard_fewsjdbc_jdbcsource')


    models = {
        'lizard_fewsjdbc.jdbcsource': {
            'Meta': {'object_name': 'JdbcSource'},
            'connector_string': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customfilter': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_tag_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'jdbc_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'usecustomfilter': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']
