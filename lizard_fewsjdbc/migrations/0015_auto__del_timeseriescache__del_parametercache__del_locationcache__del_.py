# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TimeseriesCache'
        db.delete_table('lizard_fewsjdbc_timeseriescache')

        # Deleting model 'ParameterCache'
        db.delete_table('lizard_fewsjdbc_parametercache')

        # Deleting model 'LocationCache'
        db.delete_table('lizard_fewsjdbc_locationcache')

        # Deleting model 'FilterCache'
        db.delete_table('lizard_fewsjdbc_filtercache')


    def backwards(self, orm):
        # Adding model 'TimeseriesCache'
        db.create_table('lizard_fewsjdbc_timeseriescache', (
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
            ('t_parameter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.ParameterCache'])),
            ('t_filter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.FilterCache'])),
            ('t_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.LocationCache'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['TimeseriesCache'])

        # Adding model 'ParameterCache'
        db.create_table('lizard_fewsjdbc_parametercache', (
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parameter_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parameterid', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('parameter_group', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['ParameterCache'])

        # Adding model 'LocationCache'
        db.create_table('lizard_fewsjdbc_locationcache', (
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
            ('parent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('locationid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('tooltiptext', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['LocationCache'])

        # Adding model 'FilterCache'
        db.create_table('lizard_fewsjdbc_filtercache', (
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'], null=True, blank=True)),
            ('parent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('parent_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('filterid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('is_end_node', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sub_filter', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['FilterCache'])


    models = {
        'lizard_fewsjdbc.filterrootwebrssource': {
            'Meta': {'object_name': 'FilterRootWebRSSource'},
            'filter_tree_root': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']"})
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
        'lizard_fewsjdbc.iconstylewebrs': {
            'Meta': {'object_name': 'IconStyleWebRS'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'fews_filter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_parameter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'}),
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
        },
        'lizard_fewsjdbc.webrssource': {
            'Meta': {'object_name': 'WebRSSource'},
            'base_path': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']