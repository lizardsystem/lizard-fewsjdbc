# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'IconStyle.draw_in_legend'
        db.add_column('lizard_fewsjdbc_iconstyle', 'draw_in_legend',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'IconStyle.draw_in_legend'
        db.delete_column('lizard_fewsjdbc_iconstyle', 'draw_in_legend')


    models = {
        'lizard_fewsjdbc.iconstyle': {
            'Meta': {'object_name': 'IconStyle'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'draw_in_legend': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timezone_string': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'usecustomfilter': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lizard_fewsjdbc.threshold': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Threshold'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '6'}),
            'filter_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameter_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '8'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']