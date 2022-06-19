def type_range_validator(form, range_start, range_end):
    if range_start and range_end:
        if range_start > range_end:
            form.add_error('range_start', 'Left range is smaller then right.')
            form.add_error('range_end', 'Right range is smaller then left.')
    else:
        if range_start is None:
            form.add_error('range_start', 'This field is required.')
        if range_end is None:
            form.add_error('range_end', 'This field is required.')
