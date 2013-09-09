# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TimeseriesCache'
        db.create_table('lizard_fewsjdbc_timeseriescache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('t_filter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.FilterCache'])),
            ('t_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.LocationCache'])),
            ('t_parameter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.ParameterCache'])),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['TimeseriesCache'])

        # Adding model 'WebRSSource'
        db.create_table('lizard_fewsjdbc_webrssource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('base_path', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['WebRSSource'])

        # Adding model 'ParameterCache'
        db.create_table('lizard_fewsjdbc_parametercache', (
            ('parameterid', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parameter_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parameter_group', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['ParameterCache'])

        # Adding model 'LocationCache'
        db.create_table('lizard_fewsjdbc_locationcache', (
            ('locationid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('tooltiptext', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['LocationCache'])

        # Adding model 'FilterCache'
        db.create_table('lizard_fewsjdbc_filtercache', (
            ('filterid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('is_sub_filter', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parent_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('is_end_node', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['FilterCache'])


    def backwards(self, orm):
        # Deleting model 'TimeseriesCache'
        db.delete_table('lizard_fewsjdbc_timeseriescache')

        # Deleting model 'WebRSSource'
        db.delete_table('lizard_fewsjdbc_webrssource')

        # Deleting model 'ParameterCache'
        db.delete_table('lizard_fewsjdbc_parametercache')

        # Deleting model 'LocationCache'
        db.delete_table('lizard_fewsjdbc_locationcache')

        # Deleting model 'FilterCache'
        db.delete_table('lizard_fewsjdbc_filtercache')


    models = {
        'lizard_fewsjdbc.filtercache': {
            'Meta': {'object_name': 'FilterCache'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'filterid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'is_end_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sub_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timezone_string': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'usecustomfilter': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lizard_fewsjdbc.locationcache': {
            'Meta': {'object_name': 'LocationCache'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locationid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tooltiptext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.parametercache': {
            'Meta': {'object_name': 'ParameterCache'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_group': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameterid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
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
        },
        'lizard_fewsjdbc.timeseriescache': {
            'Meta': {'object_name': 'TimeseriesCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            't_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.FilterCache']"}),
            't_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.LocationCache']"}),
            't_parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.ParameterCache']"}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.webrssource': {
            'Meta': {'object_name': 'WebRSSource'},
            'base_path': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']