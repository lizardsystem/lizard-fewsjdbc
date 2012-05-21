# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'IconStyle'
        db.create_table('lizard_fewsjdbc_iconstyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('jdbc_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.JdbcSource'], null=True, blank=True)),
            ('fews_filter', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('fews_location', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('fews_parameter', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('mask', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('color', self.gf('lizard_map.fields.ColorField')(max_length=8)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['IconStyle'])


    def backwards(self, orm):
        
        # Deleting model 'IconStyle'
        db.delete_table('lizard_fewsjdbc_iconstyle')


    models = {
        'lizard_fewsjdbc.iconstyle': {
            'Meta': {'object_name': 'IconStyle'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'fews_filter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_parameter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.JdbcSource']", 'null': 'True', 'blank': 'True'}),
            'mask': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'lizard_fewsjdbc.jdbcsource': {
            'Meta': {'object_name': 'JdbcSource'},
            'connector_string': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customfilter': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_tree_root': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_tag_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'jdbc_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'usecustomfilter': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']
