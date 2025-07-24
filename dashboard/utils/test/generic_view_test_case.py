# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from random import choice
from string import ascii_uppercase

from django.conf import settings
from django.core import serializers
from django.db.models import F
from django.urls import reverse
from django.utils.timezone import localtime
from rest_framework import status

from dashboard.utils.test.generic_test_case import GenericTestCase


class GenericViewTest(GenericTestCase):
    logger = logging.getLogger(__name__)

    app_admin_username = 'misuser'
    app_manager_username = 'useroffice'
    app_user_username = None
    app_nonauthorized_username = 'nouser'
    app_div_head_username = 'mr_burns'

    all_roles_list = [app_admin_username, app_manager_username, app_nonauthorized_username]

    def setUp(self):

        # Initialize admin and manager user

        self.model_name = ''
        self.reference_name = ''
        self.service_class = None

        self.url_new = None

        self.is_cas_authenticated = False
        self.is_authenticated = False
        self.check_unauthorized_user = False
        self.check_authorized_user_list = []

        self.check_invalid_form = True

        self.list_filter_list = [{}]
        self.list_database_query = None

        self.model_class = None
        self.form_class = None
        self.forms = []
        self.new_json_data = {}

        self.existing_object = 1
        self.not_existing_object = 9999

        self.template_directory_name = ''
        self.template_form_name = 'form.html'

        self.invalid_json_data = {'fake_attribute': 'fake_value'}
        self.create_validation = {}
        self.create_valid_json_data = {}
        self.create_excluded_validation = []

        self.mandatory_field_list = []
        self.foreignkey_field_list = []
        self.m2m_field_list = []
        self.date_field_list = []
        self.datetime_field_list = []

        # Multiple models in form
        self.form_prefix_list = []
        self.formset_prefix_list = []
        self.create_valid_json_data_related = {}
        self.model_class_related = {}

        self.update_validation = {}
        self.update_valid_json_data = {}
        self.update_excluded_validation = []
        self.update_valid_json_data_related = {}

        self.show_back_button = True
        self.show_save_button = True
        self.success_url = self.reference_name + '_list'
        self.success_url_parameter = {}

        self.related_model_name = None

        self.current_local_time = localtime()  # Just to keep localtime import due to call in eval

    def list(self, order_by=None, ascendant=None):

        url = reverse(self.reference_name + '_list')

        self.check_cas_authenticated(url)

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, url, ['GET'])
        else:
            self.allowed_http_methods_testing(url, ['GET'])

        # Should return status 200 if everything goes fine

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_queryset = response.context['object_list']

        database_queryset = self.service_class.get_all()
        if self.list_database_query:
            database_queryset = database_queryset.filter(self.list_database_query)
        if order_by:
            if ascendant:
                database_queryset = database_queryset.order_by(F(order_by).asc())
            else:
                database_queryset = database_queryset.order_by(F(order_by).desc())

        if len(database_queryset) > 10:
            # Pagination case
            self.assertEqual(len(response_queryset), 10)
        else:
            self.assertEqual(len(response_queryset), len(database_queryset))
        queryset_iterator = 0
        for object_element in response_queryset:
            self.assertEqual(object_element, database_queryset[queryset_iterator])
            queryset_iterator += 1

        # Filter testing
        for filter_args in self.list_filter_list:
            arg_string = ''
            if filter_args and len(filter_args):
                first_arg = filter_args.popitem()
                arg_string = '?%s=%s' % (first_arg[0], first_arg[1])
                for arg in filter_args:
                    arg_string += '&%s=%s' % (arg, filter_args[arg])

        url = reverse(self.reference_name + '_list') + arg_string

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_queryset = response.context['object_list']
        if hasattr(self, 'list_filter_kwargs') and self.list_filter_kwargs:
            database_queryset = self.service_class.get_filtered(filter_args, **self.list_filter_kwargs)
        else:
            database_queryset = self.service_class.get_filtered(filter_args)

        if self.list_database_query:
            database_queryset = database_queryset.filter(self.list_database_query)

        if len(database_queryset) > 10:
            # Pagination case
            self.assertEqual(len(response_queryset), 10)
        else:
            self.assertEqual(len(response_queryset), len(database_queryset))
        if order_by:
            if ascendant:
                database_queryset = database_queryset.order_by(F(order_by).asc())
            else:
                database_queryset = database_queryset.order_by(F(order_by).desc())
        queryset_iterator = 0

        for object_element in response_queryset:
            self.assertEqual(object_element, database_queryset[queryset_iterator])
            queryset_iterator += 1

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, url, 'GET')

    def detail(self, match_field_name=None):

        url = reverse(self.reference_name + '_detail', args=[self.existing_object])

        self.check_cas_authenticated(url)

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, url, ['GET'])
        else:
            self.allowed_http_methods_testing(url, ['GET'])

        # Should return status 404 for not existent object
        url = reverse(self.reference_name + '_detail', args=[self.not_existing_object])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should return status 200 if everything goes fine
        url = reverse(self.reference_name + '_detail', args=[self.existing_object])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_object = response.context['object']

        if match_field_name:
            self.assertEqual(getattr(response_object, match_field_name), self.existing_object)
        else:
            self.assertEqual(response_object.id, self.existing_object)

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, url, 'GET')

    def validate_new_register(self, create_valid_json_data, object_created, object_created_related=None):

        for key in self.create_valid_json_data.keys():

            original_key = key
            form_field_prefix = fk_field_name = None
            if self.form_prefix_list or self.forms:
                key, form_field_prefix, fk_field_name = self.get_cleaned_form_field_name(key)
            if key in self.create_excluded_validation:
                continue
            if self.is_formset_key(key):
                continue

            if key in self.foreignkey_field_list:
                eval('self.assertEqual(object_created.%s.id, create_valid_json_data[\'%s\'])' % (key, original_key))
            elif key in self.m2m_field_list:
                eval(
                    'self.assertEqual(list(map(lambda x: x.id, object_created.%s.all())), create_valid_json_data[\'%s\'])' % (
                        key, original_key))
            elif key in self.date_field_list:
                eval(
                    'self.assertEqual(object_created.%s.strftime("%%Y-%%m-%%d"), create_valid_json_data[\'%s\'])' % (
                        key, original_key))
            elif key in self.datetime_field_list:
                eval(
                    'self.assertEqual(localtime(object_created.%s).strftime("%%Y-%%m-%%d %%H:%%M:%%S"), create_valid_json_data[\'%s\'])' % (
                        key, original_key))
            elif self.create_valid_json_data_related and form_field_prefix in self.create_valid_json_data_related.keys():
                related_object_created = object_created_related[fk_field_name or form_field_prefix]
                if getattr(related_object_created, key, None) and hasattr(getattr(related_object_created, key), 'pk'):
                    eval('self.assertEqual(related_object_created.%s.pk, create_valid_json_data[\'%s\'])' % (
                        key, original_key))
                else:
                    eval('self.assertEqual(related_object_created.%s, create_valid_json_data[\'%s\'])' % (
                        key, original_key))
            else:
                eval(
                    'self.assertEqual(object_created.%s, create_valid_json_data[\'%s\'])' % (key, original_key))

    def is_formset_key(self, key):
        return any(map(lambda formset_prefix: formset_prefix in key, self.formset_prefix_list))

    def new(self):

        if not self.url_new:
            self.url_new = reverse(self.reference_name + '_new')

        self.check_cas_authenticated(self.url_new)

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, self.url_new, ['GET', 'POST', 'PUT'])
        else:
            self.allowed_http_methods_testing(self.url_new, ['GET', 'POST', 'PUT'])

        count = self.model_class.objects.count()

        # Should return status 200 if everything goes fine
        self.check_form_get_method(self.url_new, self.form_class, True)

        template_name = self.template_directory_name + self.template_form_name

        if self.check_invalid_form:

            response = self.client.post(self.url_new, self.invalid_json_data.copy())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(response.template_name[0], template_name)
            if self.forms:
                form_list_valid = [response.context['forms'][index].is_valid() for index in range(len(self.forms))]
                form_list_error_list = [response.context['forms'][index].errors for index in range(len(self.forms))]
                self.assertFalse(all(form_list_valid))
                self.assertTrue(any(form_list_error_list))
            else:
                self.assertFalse(response.context['form'].is_valid())
                self.assertTrue(response.context['form'].errors)

        if self.create_valid_json_data_related:
            original_create_valid_json_data = self.create_valid_json_data
            for model_name, model_fields in self.create_valid_json_data_related.items():
                for field, value in model_fields.items():
                    self.create_valid_json_data['{0}-{1}'.format(model_name, field)] = value

        for mandatory_field_name in self.mandatory_field_list:
            self.create_check_mandatory_fields(self.url_new, self.create_valid_json_data.copy(), mandatory_field_name,
                                               template_name)

        response = self.client.post(self.url_new, self.create_valid_json_data.copy())
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        new_count = self.model_class.objects.count()
        self.assertEqual(new_count, count + 1)

        self.object_created = self.model_class.objects.last()
        object_created_related = {}

        self.assertEqual(response.url, reverse(self.success_url, kwargs=self.get_success_url_parameter()))

        if self.model_class_related:
            for related_model in self.model_class_related.keys():
                object_created_related[related_model] = self.model_class_related[related_model].objects.last()

        self.validate_new_register(self.create_valid_json_data, self.object_created, object_created_related)

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, self.url_new, 'POST')

    def check_form_get_method(self, url, form_class, create=False):
        # Should return status 200 if everything goes fine

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if self.forms:
            my_forms = response.context['forms']
            self.assertTrue(len(my_forms) > 1)
            for index, form in enumerate(self.forms):
                self.assertIsInstance(my_forms[index], form)
            my_form = my_forms[0]
        else:
            my_form = response.context['form']
            self.assertIsInstance(my_form, self.form_class)

        if self.show_back_button:
            self.assertContains(response, self.labels.BUTTON_TEXT_BACK)
        if self.show_save_button:
            self.assertContains(response, self.labels.BUTTON_TEXT_SAVE)

        return my_form

    def create_check_mandatory_fields(self, url, json_data, mandatory_field_name, template_name):

        json_data.pop(mandatory_field_name)

        response = self.client.post(url, json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.template_name[0], template_name)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)
        if self.form_prefix_list:
            mandatory_field_name, form_field_prefix, _ = self.get_cleaned_form_field_name(mandatory_field_name)
        self.assertTrue(mandatory_field_name in response.context['form'].errors)

    def create_check_length_fields(self, url, json_data, field_name, template_name, max_length):

        json_data[field_name] = ''.join(choice(ascii_uppercase) for i in range(max_length + 1))

        if max_length == 1:
            error_message = self.field_length_exceeded_text % (max_length, (max_length + 1))
            error_message = error_message.replace('characters', 'character')
        else:
            error_message = self.field_length_exceeded_text % (max_length, (max_length + 1))

        response = self.client.post(url, json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.template_name[0], template_name)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(field_name in response.context['form'].errors)
        self.assertEqual(response.context['form'].errors[field_name][0], error_message)

    def update(self, match_field_name=None, url_suffix='_edit', check_allowed_http_methods=True):

        if match_field_name:
            url = reverse(self.reference_name + url_suffix, kwargs={match_field_name: self.existing_object})
        else:
            url = reverse(self.reference_name + url_suffix, kwargs={'pk': self.existing_object})

        self.check_cas_authenticated(url)

        if self.is_authenticated:
            self.login(self.authorized_username)
        if check_allowed_http_methods:
            self.allowed_http_methods_testing(url, ['GET', 'POST', 'PUT'])

        count = self.model_class.objects.count()

        # Should return status 404 for not existent object
        url = reverse(self.reference_name + url_suffix, args=[self.not_existing_object])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should return status 200 if everything goes fine
        url = reverse(self.reference_name + url_suffix, args=[self.existing_object])
        self.check_form_get_method(url, self.form_class, False)

        template_name = self.template_directory_name + self.template_form_name

        if self.check_invalid_form:
            response = self.client.post(url, self.invalid_json_data.copy())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(response.template_name[0], template_name)
            if self.forms:
                form_list_valid = [response.context['forms'][index].is_valid() for index in range(len(self.forms))]
                form_list_error_list = [response.context['forms'][index].errors for index in range(len(self.forms))]
                self.assertFalse(all(form_list_valid))
                self.assertTrue(any(form_list_error_list))
            else:
                self.assertFalse(response.context['form'].is_valid())
                self.assertTrue(response.context['form'].errors)

        if self.update_valid_json_data_related:
            original_update_valid_json_data = self.update_valid_json_data
            for model_name, model_fields in self.update_valid_json_data_related.items():
                for field, value in model_fields.items():
                    self.update_valid_json_data['{0}-{1}'.format(model_name, field)] = value

        for mandatory_field_name in self.mandatory_field_list:
            self.create_check_mandatory_fields(url, self.update_valid_json_data.copy(), mandatory_field_name,
                                               template_name)

        response = self.client.post(url, self.update_valid_json_data.copy(), format='multipart')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        new_count = self.model_class.objects.count()
        self.assertEqual(new_count, count)

        if match_field_name:
            query = {match_field_name: self.existing_object}
            self.object_updated = self.model_class.objects.get(**query)
        else:
            self.object_updated = self.model_class.objects.get(pk=self.existing_object)

        object_updated_related = {}
        if self.model_class_related:
            for related_model in self.model_class_related.keys():
                object_updated_related[related_model] = self.model_class_related[related_model].objects.last()
        for key in self.update_valid_json_data.keys():
            original_key = key
            form_field_prefix = fk_field_name = None
            if self.form_prefix_list or self.forms:
                key, form_field_prefix, fk_field_name = self.get_cleaned_form_field_name(key)
            if key in self.update_excluded_validation:
                continue
            if self.is_formset_key(key):
                continue

            if key in self.foreignkey_field_list:
                key_2 = original_key if self.form_prefix_list and key != original_key else key
                eval(
                    'self.assertEqual(self.object_updated.%s.id, self.update_valid_json_data[\'%s\'])' % (key, key_2))
            elif key in self.m2m_field_list:
                eval(
                    'self.assertEqual(list(map(lambda x: x.id, self.object_updated.%s.all())), self.update_valid_json_data[\'%s\'])' % (
                        key, key))
            elif key in self.date_field_list:
                eval(
                    'self.assertEqual(self.object_updated.%s.strftime("%%Y-%%m-%%d"), self.update_valid_json_data[\'%s\'])' % (
                        key, key))
            elif key in self.datetime_field_list:
                eval(
                    'self.assertEqual(localtime(self.object_updated.%s).strftime("%%Y-%%m-%%d %%H:%%M:%%S"), self.update_valid_json_data[\'%s\'])' % (
                        key, key))
            elif self.update_valid_json_data_related and form_field_prefix in self.update_valid_json_data_related.keys():
                related_object_updated = object_updated_related[fk_field_name or form_field_prefix]
                if getattr(related_object_updated, key, None) and hasattr(getattr(related_object_updated, key), 'pk'):
                    eval('self.assertEqual(related_object_updated.%s.pk, self.update_valid_json_data[\'%s\'])' % (
                        key, original_key))
                else:
                    eval('self.assertEqual(related_object_updated.%s, self.update_valid_json_data[\'%s\'])' % (
                        key, original_key))
            else:
                key_2 = original_key if self.form_prefix_list and key != original_key else key
                eval('self.assertEqual(str(self.object_updated.%s), str(self.update_valid_json_data[\'%s\']))' % (
                    key, key_2))

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, url, 'POST', cas_auth=self.is_cas_authenticated,
                             basic_auth=self.is_authenticated)

    def check_delete_get_method(self, url):
        # Should return status 200 if everything goes fine

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.labels.BUTTON_TEXT_BACK)
        self.assertContains(response, self.labels.BUTTON_TEXT_CONFIRM)

        return None

    def delete(self):

        url = reverse(self.reference_name + '_delete', args=[self.existing_object])

        self.check_cas_authenticated(url)

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, url, ['GET', 'POST', 'PUT', 'DELETE'])
        else:
            self.allowed_http_methods_testing(url, ['GET', 'POST', 'PUT', 'DELETE'])

        count = self.model_class.objects.count()

        # Should return status 404 for not existent object
        url = reverse(self.reference_name + '_delete', args=[self.not_existing_object])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should return status 200 if everything goes fine
        url = reverse(self.reference_name + '_delete', args=[self.existing_object])
        self.check_delete_get_method(url)

        template_name = self.template_directory_name + 'delete.html'

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse(self.reference_name + '_list'))

        new_count = self.model_class.objects.count()
        self.assertEqual(new_count, count - 1)

        url = reverse(self.reference_name + '_delete', args=[self.existing_object])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, url, 'DELETE')

    def download(self):

        url = reverse(self.reference_name + '_download', kwargs={'pkp': self.existing_object})

        # Test the download of the file -> Find a way to have document stored in a temp file
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.check_cas_authenticated(url)

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, url, ['GET'])
        else:
            self.allowed_http_methods_testing(url, ['GET'])

        if self.check_unauthorized_user:
            self.all_roles_list = [self.app_admin_username, self.app_manager_username]
            self.check_roles(self.check_authorized_user_list, url, 'GET', cas_auth=False)

        # Should return status 404 for not existent object
        self.login(self.authorized_username)
        url = reverse(self.reference_name + '_download', kwargs={'pkp': self.not_existing_object})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def model_formset_to_request_json(self, element_list, formset_name, field_list):

        serialized_model_json_list = json.loads(serializers.serialize('json', element_list))
        result_json = {formset_name + '-TOTAL_FORMS': len(serialized_model_json_list),
                       formset_name + '-INITIAL_FORMS': len(serialized_model_json_list),
                       formset_name + '-MIN_NUM_FORMS': '0', formset_name + '-MAX_NUM_FORMS': '1000'}
        for index, serialized_model_json in enumerate(serialized_model_json_list):
            prefix = '%s-%s-' % (formset_name, index)
            for key, value in serialized_model_json.items():
                if key == 'pk':
                    result_json[prefix + 'id'] = value
                if key == 'fields':
                    for fields_key, fields_value in value.items():
                        if fields_key in field_list:
                            result_json[prefix + fields_key] = fields_value
            result_json[prefix + 'DELETE'] = ''

        if serialized_model_json_list:
            last_element = len(serialized_model_json_list)
        else:
            last_element = 0
        return result_json, last_element

    def formset_to_request_json(self, formset_list, formset_name):

        result_json = {formset_name + '-TOTAL_FORMS': len(formset_list),
                       formset_name + '-INITIAL_FORMS': len(formset_list), formset_name + '-MIN_NUM_FORMS': '0',
                       formset_name + '-MAX_NUM_FORMS': '1000'}

        for index, formset in enumerate(formset_list):
            prefix = '%s-%s-' % (formset_name, index)
            if formset:
                for key, value in formset.data():
                    if key == 'pk':
                        result_json[prefix + 'id'] = value
                    if key == 'fields':
                        for fields_key, fields_value in value.items():
                            result_json[prefix + fields_key] = fields_value
                result_json[prefix + 'DELETE'] = ''

        if formset_list:
            last_element = len(formset_list)
        else:
            last_element = 0
        return result_json, last_element

    def get_cleaned_form_field_name(self, form_field_name):
        if self.forms:
            for form in self.forms:
                if hasattr(form, 'prefix') and form.prefix and f'{form.prefix}-' in form_field_name:
                    return form_field_name.replace(f'{form.prefix}-', ''), form.prefix, form.fk_field_name
        elif self.formset_prefix_list or self.form_prefix_list:
            prefix_list = self.formset_prefix_list if self.formset_prefix_list else self.form_prefix_list
            for form_prefix in prefix_list:
                if '{0}-'.format(form_prefix) in form_field_name:
                    form_field_name = form_field_name.replace('{0}-'.format(form_prefix), '')
                    return form_field_name, form_prefix, None
        return form_field_name, None, None

    def get_success_url_parameter(self, **kwargs):
        return self.success_url_parameter

    def check_cas_authenticated(self, url):
        if self.is_cas_authenticated:
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.is_authenticated = True

    def deleteREST(self, is_logic=True, slug_object_selector=False):

        if slug_object_selector:
            url = reverse(self.reference_name + '_delete', args=[self.existing_object])
        else:
            url = reverse(self.reference_name + '_delete', args=self.existing_object)
        if self.is_cas_authenticated:
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.is_authenticated = True

        if self.is_authenticated:
            self.login_and_check_http_methods(self.authorized_username, url, ['DELETE'])
        else:
            self.allowed_http_methods_testing(url, ['DELETE'])

        # Test with invalid id
        if slug_object_selector:
            url = reverse(self.reference_name + '_delete', args=[self.invalid_id])
        else:
            url = reverse(self.reference_name + '_delete', args=self.invalid_id)

        response = self.client.delete(url, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test with non-existent id
        if slug_object_selector:
            url = reverse(self.reference_name + '_delete', args=[self.not_existing_object])
        else:
            url = reverse(self.reference_name + '_delete', args=self.not_existing_object)

        response = self.client.delete(url, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        json_content = json.loads(response.content)

        self.check_mandatory_response_error(json_content)

        # Getting initial register number
        count = self.model_class.objects.count()

        if slug_object_selector:
            url = reverse(self.reference_name + '_delete', args=[self.existing_object])
        else:
            url = reverse(self.reference_name + '_delete', args=self.existing_object)

        response = self.client.delete(url, format='json', content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Checking if the register was deleted
        new_count = self.model_class.objects.count()
        if is_logic:
            self.assertEquals(new_count, count)
        else:
            self.assertEquals(new_count, (count - 1))

        if self.check_unauthorized_user:
            self.check_roles(self.check_authorized_user_list, url, 'DELETE')
