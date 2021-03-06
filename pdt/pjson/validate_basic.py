#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
# Written by Alan Viars

import json
import sys
import datetime
import re
from choices import COUNTRIES, STATES
MIN_AGE_IN_DAYS = 6570


def validate_basic_dict(d, enumeration_type, action, number=None):
    """
    Input a python dict(d) object. Return a list of errors. If error list
    is empty then basic section is valid.
    """
    errors = []
    warnings = []
    # check values do not exceed max length

    max_values = {
        'name_prefix': 5,
        'first_name': 150,
        'last_name': 150,
        'middle_name': 150,
        'name_sufix': 5,
        'credential': 50,
        'doing_business_as': 300,
        'sole_proprieter': 3,
        'organization_name': 300,
        'organization_other_name': 300,
        'organization_other_name_code': 1,
        'ssn': 9,
        'ein': 9,
        'itin': 9,
        'gender': 1,
        'state_of_birth': 2,
        'country_of_birth': 2,
        'mode': 1,
        'status': 1,
        'contact_method': 1,
        'classification': 1,
        'deactivated_details': 1024,
        'deactivation_reason_code': 2,
        'deceased_notes': 1024,
        'parent_organization_npi': 9,
        'parent_organization_ein': 9,
        'parent_organization_legal_business_name': 300,
        'reactivation_note': 1024,
        'comments': 1024,
        'contact_person_credential': 20,
        'contact_person_email': 75,
        'contact_person_first_name': 150,
        'contact_person_last_name': 150,
        'contact_person_middle_name': 150,
        'contact_person_prefix': 5,
        'contact_person_suffix': 4,
        'contact_person_telephone_extension': 10,
        'contact_person_telephone_number': 12,
        'contact_person_title_or_position': 150,
        'authorized_official_credential': 50,
        'authorized_official_email': 75,
        'authorized_official_first_name': 300,
        'authorized_official_last_name': 300,
        'authorized_official_middle_name': 300,
        'authorized_official_prefix': 4,
        'authorized_official_suffix': 5,
        'authorized_official_telephone_number': 12,
        'authorized_official_telephone_extension': 12,
        'authorized_official_title_or_position': 300,
        'website': 1024,
        'gravatar_email': 200,
        'facebook_handle': 100,
        'twitter_handle': 100,
        'public_email': 75,
        'driving_directions': 1024,
        'bio_headline': 256,
    }

    for k in max_values.keys():
        if d.get(k):

            cleaned_value = d.get(k, "").encode(
                'ascii', 'ignore').decode('ascii')
            if max_values[k] < len(cleaned_value):
                error = "%s exceeds max allowable length of %s." % (
                    k, max_values[k])
                errors.append(error)

    # Validate Common items ------------------------------------------

    if d.get('enumeration_date'):
        try:
            date = datetime.datetime.strptime(
                d.get('enumeration_date'), '%Y-%m-%d').date()
        except ValueError:
            error = "enumeration_date must be in YYYY-MM-DD format."
            errors.append(error)
        if action != "public":
            warning = "Enumeration date is generated by CMS. The provided value will be ignored."
            warnings.append(warning)

    if d.get('last_updated'):
        try:
            date = datetime.datetime.strptime(
                d.get('last_updated'), '%Y-%m-%d').date()
        except ValueError:
            error = "last_updated must be in YYYY-MM-DD format."
            errors.append(error)

        if action != "public":
            warning = "Last updated date is generated by CMS. The provided value will be ignored."
            warnings.append(warning)

    if d.get('initial_enumeration_date'):
        try:
            date = datetime.datetime.strptime(
                d.get('initial_enumeration_date'), '%Y-%m-%d').date()
        except ValueError:
            error = "initial_enumeration_date must be in YYYY-MM-DD format."
            errors.append(error)
        if action != "public":
            warning = "Initial enumeration date is generated by CMS. The provided value will be ignored."
            warnings.append(warning)

    if d.get('date_of_death'):
        try:
            date = datetime.datetime.strptime(
                d.get('date_of_death'), '%Y-%m-%d').date()
        except ValueError:
            error = "date_of_death must be in YYYY-MM-DD format."
            errors.append(error)
        if action != "public":
            warning = "Date of death is determined by the SSA. The provided value will be ignored."
            warnings.append(warning)

    if d.get('reactivation_date'):
        try:
            date = datetime.datetime.strptime(
                d.get('reactivation_date'), '%Y-%m-%d').date()
        except ValueError:
            error = "reactivation_date must be in YYYY-MM-DD format."
            errors.append(error)

        if action != "public":
            warning = "Reactivation date is generated by CMS. the provided value will be ignored."
            warnings.append(warning)

    if d.get('deactivation_date'):
        try:
            date = datetime.datetime.strptime(
                d.get('deactivation_date'), '%Y-%m-%d').date()
        except ValueError:
            error = "deactivation_date must be in YYYY-MM-DD format."
            errors.append(error)

        if action != "public":
            warning = "Deactivation date is generated by CMS. The provided value will be ignored."
            warnings.append(warning)

    # validate phone numbers

    if d.get('contact_person_telephone_number') and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', d.get('contact_person_telephone_number')):
        error = "contact_person_telephone_number must be in XXX-XXX-XXXX format."
        errors.append(error)

    # Meta fields -----------------------------------
    if d.get("mode") and d.get("mode", "").upper() not in ('W', 'P', 'E', 'A'):
        # Note this should always be (E)lectronic if submitting via API
        error = "mode must be in ('W','P','E', 'A')."
        errors.append(error)

    if d.get("mode") and d.get("mode") != 'A':
        # Note this should always be (E)lectronic if submitting via API
        warning = "The mode should be set to A when using the API."
        warnings.append(warning)

    if d.get("status") and d.get("status").upper() not in ('E', 'P', 'A', 'D', 'R'):

        # Note: NPPES will ignore this since status is decided by NPPES.
        error = "status must be in ('E', 'P', 'A', 'D', 'R')."
        errors.append(error)

    if d.get("status"):
        if action != "public":
            warning = "status is determined by CMS. The provided value will be ignored."
            warnings.append(warning)

    if d.get("contact_method") and d.get("contact_method") not in ('M', 'E',):
        if action != "public":
            # Note: NPPES will ignore this since status is decided by NPPES.
            error = "contact_method must be in ('M', 'E')."
            errors.append(error)

    # NPI-1 -------------------------------------------------------------------
    if enumeration_type == "NPI-1":
        # Ensure required fields for NPI-1

        if not d.get('first_name'):
            error = "first_name is required."
            errors.append(error)

        if not d.get('last_name'):
            error = "last_name is required."
            errors.append(error)

        if d.get("name_suffix") and d.get("name_suffix").upper() not in ('JR.', 'SR.', 'I', 'II', 'III', 'IV',
                                                                         'V', 'VI', 'VII', 'VIII', 'IX', 'X'):
            error = """name_suffix must be in ['Jr.', 'Sr.', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']'
            """
            errors.append(error)

        if not d.get('sole_proprietor'):
            error = "sole_proprietor is required and must be in ('YES', 'NO')."
            errors.append(error)
        else:
            if d.get('sole_proprietor').upper() not in ("YES", "NO"):
                error = "sole_proprietor must be in ('YES', 'NO')."
                errors.append(error)
        # Gender
        if action == "create" and not d.get('gender'):
            error = "gender is required."
            errors.append(error)

        elif action == "create" and d.get('gender'):
            if d.get('gender') not in ("M", "F", "T"):
                error = "gender must be in ('F','M', 'T')."
                errors.append(error)

        elif action == "update" and d.get('gender'):
            warning = "gender cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        # Date of Birth
        if action == "create" and not d.get('date_of_birth'):
            error = "date_of_birth is required when creating a new individual's record."
            errors.append(error)

        elif action == "update" and d.get('date_of_birth'):
            warning = "date_of_birth cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        elif action == "create" and d.get('date_of_birth'):
            # date supplied so let's make sure it is valid
            try:
                date_of_birth = datetime.datetime.strptime(
                    d.get('date_of_birth'), '%Y-%m-%d').date()

                age_days = datetime.date.today() - date_of_birth
                if age_days.days < MIN_AGE_IN_DAYS:
                    errors.append(
                        "Candidate must be at least 16 years of age.")

            except ValueError:
                error = "date_of_birth must be in YYYY-MM-DD format."
                errors.append(error)

        # State of Birth
        if action == "create" and not d.get('state_of_birth'):
            error = "state_of_birth is required. Use ZZ if born outside the US."
            errors.append(error)
        elif action == "create" and d.get('state_of_birth'):
            if d.get('state_of_birth') not in STATES:
                error = "state_of_birth must be 2 letter ISO code or ZZ for foreign born."
                errors.append(error)
        elif action == "update" and d.get('state_of_birth'):
            warning = "state_of_birth cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        # Country of Birth
        if action == "create" and not d.get('country_of_birth'):
            error = "country_of_birth is required for NPI-1 creation.."
            errors.append(error)
        elif action == "create" and d.get('country_of_birth'):
            if d.get('country_of_birth') not in COUNTRIES:
                error = "country_of_birth must be 2 letter ISO code."
                errors.append(error)
        elif action == "update" and d.get('country_of_birth'):
            warning = "country_of_birth cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        # Validate the interdependecies
        if d.get('country_of_birth') and d.get('country_of_birth') and \
                (d.get('country_of_birth')) != "US" and (d.get('state_of_birth') != "ZZ"):
            error = """country_of_birth and state_of_birth mismatch. A person cannot be born in both a foreign contry and a US state at the same time."""
            errors.append(error)

        if action == "create" and not d.get('ssn') and not d.get('itin'):
            error = "An NPI-1 individual provider must supppy either an SSN or an EIN."
            errors.append(error)

        if action == "update" and d.get('ssn'):
            warning = "Social security number (ssn) cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        if action == "update" and d.get('itin'):
            warning = "Individual Taxpayer Identification Number (itin) cannot be updated via API. Please contact the Enumerator help desk. The provided value will be ignored."
            warnings.append(warning)

        if d.get('ssn') and len(str(d.get('ssn'))) != 9:
            error = "SSN must be 9 digits."
            errors.append(error)

        if d.get('itin') and len(str(d.get('itin'))) != 9:
            error = "ITIN must be 9 digits."
            errors.append(error)

        # ensure a contact person is given
        if not d.get('contact_person_email'):
            if action != "public":
                error = "contact_person_email must be provided."
                errors.append(error)

        # ensure a contact person is given
        if not d.get('contact_person_first_name'):
            if action != "public":
                error = "contact_person_first_name must be provided."
                errors.append(error)

        # ensure a contact person is given
        if not d.get('contact_person_last_name'):
            if action != "public":
                error = "contact_person_last_name must be provided."
                errors.append(error)

        # ensure a contact person is given
        if not d.get('contact_person_telephone_number'):
            if action != "public":
                error = "contact_person_telephone_number must be provided."
                errors.append(error)

        # Validate the not required items NPI-1

        if d.get("name_prefix") and d.get("name_prefix").upper() not in ('MS.', 'MR.', 'MISS',
                                                                         'MRS.', 'DR.', 'PROF.'):
            error = "name_prefix  must be one of the following: 'MS.', 'MR.', 'MISS', 'MRS.', 'DR.', 'PROF.'"
            errors.append(error)

    if enumeration_type == "NPI-2":
        # Validate the organization
        if not d.get('organization_name', ""):
            error = "organization_name is required for a type 2 (organization) NPI."
            errors.append(error)
        else:
            if len(d.get('organization_name')) > 300:
                error = "organization_name is longer than allowed."
                errors.append(error)

        if action != "public":
            if not d.get('ein'):
                error = "EIN is required for a type-2 organization provider."
                errors.append(error)

        if d.get('ein') and len(str(d.get('ein'))) != 9:
            error = "EIN must be 9 digits."
            errors.append(error)

        if d.get('authorized_official_telephone_number') and not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', d.get('authorized_official_telephone_number')):
            error = "authorized_official_telephone_number must be in XXX-XXX-XXXX format."
            errors.append(error)

        if not d.get('authorized_official_first_name'):
            error = "authorized_official_first_name is required for a type-2 organization provider."
            errors.append(error)

        if not d.get('authorized_official_last_name'):
            error = "authorized_official_last_name is required for a type-2 organization provider."
            errors.append(error)

        if not d.get('authorized_official_title_or_position'):
            error = "authorized_official_title_or_position is required for a type-2 organization provider."
            errors.append(error)

        if not d.get('authorized_official_telephone_number'):
            error = "authorized_official_telephone_number is required for a type-2 organization provider."
            errors.append(error)
    retval = [errors, warnings]
    return retval
