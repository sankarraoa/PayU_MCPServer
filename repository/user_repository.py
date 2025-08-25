#repository/user_repository.py

from typing import List, Dict, Any
from sqlalchemy.engine import Connection
from sqlalchemy.sql import text
import re
import json
import re
from sqlalchemy.sql import text
from typing import List, Dict, Any

import re
from sqlalchemy.sql import text
from typing import List, Dict, Any

def get_users(conn, search_term: str) -> List[Dict[str, Any]]:
    #print(f"[DEBUG] [get_users] Called with search_term: {search_term}")

    base_query = """
    SELECT DISTINCT
        um.id,
        um.customer_id,
        um.name,
        um.first_name,
        um.middle_name,
        um.last_name,
        um.gender,
        um.date_of_birth,
        um.email_id,
        um.phone_id,
        up.number AS pan_number,
        up.nsdl_name,
        ua.embedded_data->'photo'->>'document_image' AS document_image
    FROM users_masteruser um
    LEFT JOIN users_pan up ON up.master_user_id = um.id AND up.is_valid = true
    LEFT JOIN users_aadhaar ua ON ua.master_user_id = um.id AND ua.is_valid = true
    """

    numeric = re.fullmatch(r'\d+', search_term)
    plus91 = re.fullmatch(r'\+91\d{10}', search_term)
    email_like = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", search_term)

    if numeric:   # Indian 10-digit number
        phone_term = f"+91{search_term}"
        where_clause = """
        WHERE (
            um.phone_id = :phone_term OR
            um.id = :term
        )
        """
        params = {"phone_term": phone_term, "term": int(search_term)}
    elif plus91:
        where_clause = """
        WHERE (
            um.phone_id = :phone_term OR
            um.id = :id_term
        )
        """
        # remove '+'
        id_part = search_term[3:] if search_term[3:].isdigit() else None
        params = {"phone_term": search_term, "id_term": int(id_part) if id_part else -1}
    elif email_like:
        where_clause = "WHERE um.email_id = :term"
        params = {"term": search_term}
    else:
        where_clause = """
        WHERE (
            um.name ILIKE :like_term OR
            um.first_name ILIKE :like_term OR
            um.middle_name ILIKE :like_term OR
            um.last_name ILIKE :like_term OR
            up.nsdl_name ILIKE :like_term
        )
        """
        params = {"like_term": f"%{search_term}%"}

    full_query = base_query + where_clause
    print(f" Querying users with params: {where_clause}")

    result = conn.execute(text(full_query), params)
    rows = [dict(row._mapping) for row in result]
    #print(f"[DEBUG] [get_users] Found {len(rows)} user(s)")
    return rows

def get_additional_info(conn: Connection, user_id: int) -> dict:
    query = """
    SELECT DISTINCT 
        user_master.id AS user_id, 
        user_master.customer_id AS customer_id, 
        user_master.gender AS gender, 
        user_master.date_of_birth AS dob, 
        user_master.um_uuid AS user_uuid,
        user_extra.mother_name AS mother_name,
        user_extra.alternate_phone AS alternate_contact_number, 
        user_extra.community AS community_group, 
        user_extra.marital_status AS marital_status,
        user_extra.educational_qualification AS education_level,
        user_extra.spouse_name AS spouse_name,
        user_extra.category AS beneficiary_category,
        user_extra.father_name AS father_name
    FROM users_masteruser user_master
    LEFT JOIN users_pan user_pan 
        ON user_pan.master_user_id = user_master.id 
        AND user_pan.is_valid = true
    LEFT JOIN users_masteruserextra user_extra 
        ON user_extra.master_user_id = user_master.id
    WHERE user_master.id = :user_id
    LIMIT 1
    """
    result = conn.execute(text(query), {"user_id": user_id})
    row = result.fetchone()
    return dict(row._mapping) if row else {}

def get_user_pans(conn: Connection, user_id: int):
    """
    Fetch all PAN records for a given user ID.
    Returns a list of dicts (one per PAN).
    """
    query = """
        SELECT 
            id,
            nsdl_valid, 
            number, 
            date_of_birth, 
            is_valid, 
            created_at, 
            nsdl_name, 
            status,
            CASE 
                WHEN status = 10 THEN 'Pending'
                WHEN status = 20 THEN 'Completed'
                WHEN status = 30 THEN 'PreApproved'
                WHEN status = 40 THEN 'Approved'
                WHEN status = 50 THEN 'Rejected'
                WHEN status = 100 THEN 'Expired'
                ELSE 'Unknown Status'
            END AS status_text, 
            gender 
        FROM users_pan  
        WHERE master_user_id = :user_id
        ORDER BY created_at DESC;
    """
    result = conn.execute(text(query), {"user_id": user_id})
    print(result)
    return [dict(row._mapping) for row in result]

def mask_aadhaar(aadhaar):
    """Format Aadhaar as xxxx-xxxx-1234 (assuming input is last 4 digits)."""
    if aadhaar and len(str(aadhaar)) == 4:
        return f"xxxx-xxxx-{aadhaar}"
    return aadhaar

def get_user_aadhaar_kyc(conn, user_id):
    query = """
    SELECT
        ukv.expiry_date AS kyc_expiry_date,
        ukv.mode AS kyc_mode,
        ukv.ckyc_id AS kyc_ckyc_id,
        ukv.source_id AS kyc_source_id,
        ukv.is_valid AS kyc_is_valid,
        ua.gender AS aadhaar_gender,
        ua.digits AS aadhaar_digits,
        ua.phone_linked AS aadhaar_phone_linked,
        ua.name AS aadhaar_name,
        ua.is_valid AS aadhaar_is_valid,
        ua.address_id AS aadhaar_address_id,
        ua.date_of_birth AS aadhaar_date_of_birth,
        ua.is_verification_skipped AS aadhaar_verification_skipped,
        CASE
            WHEN ua.status = 10 THEN 'Pending'
            WHEN ua.status = 15 THEN 'Completed'
            WHEN ua.status = 20 THEN 'Submitted'
            WHEN ua.status = 30 THEN 'PreApproved'
            WHEN ua.status = 40 THEN 'Approved'
            WHEN ua.status = 50 THEN 'Rejected'
            WHEN ua.status = 100 THEN 'Expired'
            WHEN ua.status = 150 THEN 'Frozen'
            ELSE 'Unknown'
        END AS aadhaar_status,
        ua.embedded_data AS aadhaar_embedded_data
    FROM users_kycverification ukv
    LEFT JOIN users_aadhaar ua
        ON ukv.master_user_id = ua.master_user_id
        AND ukv.aadhaar_id = ua.id
    WHERE
        ukv.master_user_id = :user_id
        AND ukv.mode IN (1, 2, 4, 5)
        AND ua.is_valid = true
    """
    row = conn.execute(text(query), {"user_id": user_id}).fetchone()
    if not row:
        return {}
    data = dict(row._mapping)
    embedded = data.get('aadhaar_embedded_data')
    if embedded:
        if isinstance(embedded, str):
            embedded_json = json.loads(embedded)
        elif isinstance(embedded, dict):
            embedded_json = embedded
        else:
            embedded_json = {}
        document_image = (
            embedded_json.get('photo', {}).get('document_image')
            or embedded_json.get('document_image')
        )
        careof = embedded_json.get('original_kyc_info', {}).get('careof')
        address = embedded_json.get('original_kyc_info', {}).get('address')
        ts = embedded_json.get('ts')
    else:
        document_image = careof = address = ts = None

    return {
        "aadhaar_photo_b64": document_image,
        "aadhaar_masked": mask_aadhaar(data.get('aadhaar_digits')),
        "aadhaar_status": data.get('aadhaar_status'),
        "aadhaar_name": data.get('aadhaar_name'),
        "aadhaar_dob": data.get('aadhaar_date_of_birth'),
        "aadhaar_gender": data.get('aadhaar_gender'),
        "aadhaar_date_verified": ts,
        "aadhaar_careof": careof,
        "aadhaar_address": address,
    }

def get_user_ckyc(conn, user_id):
    query = """
        SELECT
            ukv.mode AS kyc_mode,
            ukv.ckyc_id AS kyc_ckyc_id,
            ukv.expiry_date AS kyc_expiry_date,
            ukv.source_id AS kyc_source_id,
            ukv.is_valid AS kyc_is_valid,
            uc.ckyc_data_origin AS ckyc_ckyc_data_origin,
            uc.aadhaar_digits AS ckyc_aadhaar_digits,
            uc.base_search_type AS ckyc_base_search_type,
            uc.base_search_value AS ckyc_base_search_value,
            uc.document_ids AS ckyc_document_ids,
            uc.is_confirmed AS ckyc_is_confirmed,
            uc.is_valid AS ckyc_is_valid,
            CASE
                WHEN uc.status = 10 THEN 'Pending'
                WHEN uc.status = 15 THEN 'Completed'
                WHEN uc.status = 20 THEN 'Submitted'
                WHEN uc.status = 30 THEN 'PreApproved'
                WHEN uc.status = 40 THEN 'Approved'
                WHEN uc.status = 50 THEN 'Rejected'
                WHEN uc.status = 100 THEN 'Expired'
                WHEN uc.status = 150 THEN 'Frozen'
                ELSE 'Unknown'
            END AS ckyc_status,
            uc.phone AS ckyc_phone,
            uc.validation_failures AS ckyc_validation_failures,
            uc.number AS ckyc_number,
            uc.auth_factor_value AS ckyc_auth_factor_value,
            uc.ckyc_source AS ckyc_ckyc_source,
            uc.details AS ckyc_details
        FROM
            users_kycverification ukv
        LEFT JOIN
            users_ckyc uc
            ON ukv.master_user_id = uc.master_user_id
        WHERE
            ukv.master_user_id = :user_id
            AND ukv.mode = 3
            AND uc.is_valid = true
        """

    row = conn.execute(text(query), {"user_id": user_id}).fetchone()
    if not row:
        return {}
    data = dict(row._mapping)
    ckyc_details_str = data.get('ckyc_details')
    if ckyc_details_str:
        if isinstance(ckyc_details_str, str):
            ckyc_details_json = json.loads(ckyc_details_str)
        elif isinstance(ckyc_details_str, dict):
            ckyc_details_json = ckyc_details_str
        else:
            ckyc_details_json = {}
        search = ckyc_details_json.get('search', {})
        ckyc_name = search.get('NAME')
        ckyc_kyc_date = search.get('KYC_DATE')
        ckyc_father = search.get('FATHERS_NAME')
    else:
        ckyc_name = ckyc_kyc_date = ckyc_father = None
    # For documents: show icon if document ids present
    has_documents = bool(data.get('ckyc_document_ids'))
    return {
        "ckyc_number": data.get('ckyc_number'),
        "ckyc_masked_aadhaar": mask_aadhaar(data.get('ckyc_aadhaar_digits')),
        "ckyc_phone": data.get('ckyc_phone'),
        "ckyc_date_extracted": ckyc_kyc_date,
        "ckyc_father_name": ckyc_father,
        "ckyc_status": data.get('ckyc_status'),
        "ckyc_has_documents": has_documents,
    }

def get_user_header_details(conn: Connection, user_id: int) -> dict:
    query = """
    SELECT DISTINCT 
        user_master.id AS user_id, 
        user_master.name AS full_name, 
        user_master.first_name AS first_name, 
        user_master.middle_name AS middle_name, 
        user_master.last_name AS last_name, 
        user_master.email_id AS email_address, 
        user_master.phone_id AS phone_id, 
        user_pan.number AS pan_number, 
        user_aadhaar.digits AS aadhaar_digits, 
        user_aadhaar.embedded_data->'photo'->>'document_image' AS document_image,
        user_phone.phone AS phone_number, 
        user_phone.otp_verified_at AS otp_verification_time,
        user_email.verified_at AS email_verified_at, 
        user_aadhaar.is_valid, 
        user_pan.is_valid,
        users_aml.decision As aml_isHit
    FROM users_masteruser user_master
    LEFT JOIN users_pan user_pan 
        ON user_pan.master_user_id = user_master.id 
        AND user_pan.is_valid = true
    LEFT JOIN users_masteruserextra user_extra 
        ON user_extra.master_user_id = user_master.id
    LEFT JOIN users_aadhaar user_aadhaar 
        ON user_aadhaar.master_user_id = user_master.id 
        AND user_aadhaar.is_valid = true
    LEFT JOIN users_phonenumber user_phone 
        ON user_phone.phone = user_master.phone_id
    LEFT JOIN users_email user_email
        ON user_email.email = user_master.email_id
    LEFT JOIN users_amlresponsedata users_aml 
        ON users_aml.master_user_id = user_master.id     
    WHERE user_master.id = :user_id 
    LIMIT 1
    """
    result = conn.execute(text(query), {"user_id": user_id})
    row = result.fetchone()
    return dict(row._mapping) if row else {}

def get_aml_details(conn: Connection, user_id: int) -> dict:
    query = """
        SELECT 
            users_aml_log.response::json->'ScreeningRequestData'->'ScreeningResults'->>'Matched' AS matched_status,
            users_aml_log.response::json->'ScreeningRequestData'->'ScreeningResults'->>'AlertCount' AS alert_count,
            users_aml_log.response::json->'ScreeningRequestData'->'ScreeningResults'->'Alerts' AS alerts,
            users_aml_log.response::json->'ScreeningRequestData'->'ScreeningResults'->>'ReportData' AS report_data,
            users_aml.decision AS aml_isHit
        FROM users_masteruser user_master
        LEFT JOIN users_amlresponsedata users_aml 
            ON users_aml.master_user_id = user_master.id     
        LEFT JOIN users_amlrequestresponselog users_aml_log
            ON users_aml.application_id = users_aml_log.application_id     
        WHERE user_master.id = :user_id 
        LIMIT 1
    """
    result = conn.execute(text(query), {"user_id": user_id})
    row = result.fetchone()
    return dict(row._mapping) if row else {}

def get_user_address(conn: Connection, user_id: int) -> dict:
    query = """
        SELECT 
            address_type,
            line1,
            line2,
            city,
            state,
            status,
            postal_code_id,
            landmark,
            id, 
            linked_id,
            is_valid
        FROM users_address 
        WHERE master_user_id = :user_id AND is_valid = true
    """
    result = conn.execute(text(query), {"user_id": user_id})
    addresses = [dict(row._mapping) for row in result]
    # Map address_type: 1 = current, 2 = communication
    addrs = {1: None, 2: None}
    for addr in addresses:
        if addr['address_type'] in [1, 2]:
            addrs[addr['address_type']] = addr
    return addrs  # {1: <current>, 2: <communication>}

