function hideRangeWidgets(rangeWidgets) {
    for (let widget of rangeWidgets) {
        var rangeInput = widget.querySelector('input');
        rangeInput.value = '';
        widget.style.display = 'none';
    }
}

function addSchemaColumnForm() {
    let columnForms = document.querySelectorAll(".column_form");
    let totalForms = document.querySelector("#id_form-TOTAL_FORMS");
    let formsetTable = document.querySelector("#formset_table_body");
    let newForm = columnForms[0].cloneNode(true);
    formsetTable.append(newForm);

    updateAllColumnFormsId();
    clearFormErrors(newForm);
    clearFormInputs(newForm);
    hideRangeWidgets(newForm.getElementsByClassName("range_widget"));
    attachListenerToInnerSelects(newForm);

    let columnFormsUpdated = document.querySelectorAll(".column_form");
    totalForms.setAttribute('value', `${columnFormsUpdated.length}`);
    document.getElementById('schema_btn').scrollIntoView();
}

function updateAllColumnFormsId() {
    let columnForms = document.querySelectorAll(".column_form");

    let formRegex = RegExp(`form-(\\d)+-`, 'g');

    for (let i = 0; i < columnForms.length; i++) {
        let formChilds = columnForms[i].getElementsByTagName('*');
        for (let child of formChilds) {
            child.id = child.id.replace(formRegex, `form-${i}-`);
            let childName = child.getAttribute("name");
            if (childName) {
                childName = childName.replace(formRegex, `form-${i}-`);
                child.setAttribute("name", childName);
            }
        }
    }
}

function clearFormInputs(element) {
    var charInput = element.querySelectorAll('input');
    var selectInput = element.querySelectorAll('select');
    charInput.forEach(obj => obj.value = '');
    selectInput.forEach(obj => obj.selectedIndex = 0);
    var formHiddenId = element.querySelector('[id$="-id"]');
    formHiddenId.value = ''
}

function clearFormErrors(form) {
    inputError = form.querySelectorAll('.errorlist');
    inputError.forEach(item => item.remove());
}

function deleteSchemaColumn(btn) {
    if (document.querySelectorAll(".column_form").length > 1) {
        var currentForm = btn.closest('.column_form');
        currentForm.remove();
        let columnForms = document.querySelectorAll(".column_form");
        let totalForms = document.querySelector("#id_form-TOTAL_FORMS");
        totalForms.setAttribute('value', `${columnForms.length}`);
        updateAllColumnFormsId();
    }
}

function dataTypeWidgetListener(item) {
    var rangeWidgets = item.parentNode.parentNode.getElementsByClassName("range_widget");
    hideRangeWidgets(rangeWidgets);
    let dataType = dataTypes.find(obj => obj.id === item.value);
    if (dataType && dataType.ranged === 'True') {
        for (let widget of rangeWidgets) {
            widget.style.display = 'block';
        }
    }
}

function attachListenerToInnerSelects(element) {
    let dataTypesSelectsList = element.querySelectorAll('[id^="id_form-"][id$="-type"]');
    dataTypesSelectsList.forEach(item => item.addEventListener("change", function () {
        dataTypeWidgetListener(item)
    }));
}

function showRangesOnWindowLoad() {
    let columnForms = document.querySelectorAll(".column_form");
    for (let form of columnForms) {
        let selectedIndex = form.querySelector('.column_type select').selectedIndex;
        let rangeWidges = form.querySelectorAll('.range_widget')
        let dataType = dataTypes.find(item => parseInt(item.id) === selectedIndex);
        if (dataType && dataType.ranged === 'True') {
            rangeWidges.forEach(item => item.style.display = 'block');
        }
    }
}

window.onload = function () {
    attachListenerToInnerSelects(document);
    showRangesOnWindowLoad();
    var initialForms = document.querySelector("#id_form-INITIAL_FORMS");
    initialForms.setAttribute('value', 0);
};