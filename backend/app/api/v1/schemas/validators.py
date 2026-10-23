from db.models import LinkTypeEnum


def validate_link_type_dependencies(values, validate_all=True):
    if isinstance(values, dict):
        link_type = values.get('link_type')
        link = values.get('link')
        page_id = values.get('page_id')

        if link_type is None and validate_all:
            link_type = LinkTypeEnum.EXTERNAL  # default

        if link_type is not None:
            if link_type == LinkTypeEnum.EXTERNAL:
                if not link:
                    raise ValueError('link field is required when link_type is EXTERNAL')
            elif link_type == LinkTypeEnum.INTERNAL_PAGE:
                if not page_id:
                    raise ValueError('page_id field is required when link_type is INTERNAL_PAGE')

    return values


def validate_header_image_dependencies(page_type, header_image):
    if page_type == "HEADERED":
        if not header_image:
            raise ValueError("header_image field must be provided when page type is HEADERED")
    elif header_image:
        raise ValueError("header_image field should be null when page type is not HEADERED")
    return header_image