/******************************************************************************
 * djangoFCM — Django app which stores, manages FCM push tokens               *
 * and interacts with them.                                                   *
 * Copyright (C) 2021-2021 omelched                                           *
 *                                                                            *
 * This file is part of djangoFCM.                                            *
 *                                                                            *
 * djangoFCM is free software: you can redistribute it and/or modify          *
 * it under the terms of the GNU Affero General Public License as published   *
 * by the Free Software Foundation, either version 3 of the License, or       *
 * (at your option) any later version.                                        *
 *                                                                            *
 * djangoFCM is distributed in the hope that it will be useful,               *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of             *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
 * GNU Affero General Public License for more details.                        *
 *                                                                            *
 * You should have received a copy of the GNU Affero General Public License   *
 * along with djangoFCM.  If not, see <https://www.gnu.org/licenses/>.        *
 ******************************************************************************/

const $ = django.jQuery

let metadata = [];

if( typeof Element.prototype.clearChildren === 'undefined' ) {
    Object.defineProperty(Element.prototype, 'clearChildren', {
      configurable: true,
      enumerable: false,
      value: function() {
        while(this.firstChild) this.removeChild(this.lastChild);
      }
    });
}

function formset() {

  const prefix = $("table.composer").data("prefix");
  const totalFormsSelector = "#id_" + prefix + "-TOTAL_FORMS";
  const totalForms = $(totalFormsSelector).prop("autocomplete", "off");
  const maxForms = $("#id_" + prefix + "-MAX_NUM_FORMS").prop("autocomplete", "off");
  const formCssClass = "dynamic-form";
  let nextIndex = parseInt(totalForms.val(), 10);

  function addRowHandler(e) {
    e.preventDefault();
    let template = $(".composer tr.template_row");
    let row = template.clone(true);
    row.removeClass("template_row").addClass(formCssClass);
    row.find("*").each(function() {
      updateElementIndex(this, totalForms.val());
    });
    row.insertBefore($(template));
    renderStates();

    $(totalForms).val(parseInt(totalForms.val(), 10) + 1);
    nextIndex += 1;

    if ((maxForms.val() !== '') && (maxForms.val() - totalForms.val()) <= 0) {
      addButton.parent().hide();
    }

  }

  function deleteRowHandler(e) {
    e.preventDefault();
    let deleteButton = $(e.target);
    let row = deleteButton.parent().parent();
    row.remove();
    renderStates();
    nextIndex -= 1;
    const forms = $("." + formCssClass);
    $(totalFormsSelector).val(forms.length);

    let i, formCount;
    const updateElementCallback = function() {
      updateElementIndex(this, i);
    };
    for (i = 0, formCount = forms.length; i < formCount; i++) {
      updateElementIndex($(forms).get(i), i);
      $(forms.get(i)).find("*").each(updateElementCallback);
    }
    if ((maxForms.val() === '') || (maxForms.val() - forms.length) > 0) {
      addButton.parent().show();
    }
  }

  function switchStates(e) {
    e.preventDefault();
    let switchStateButton = $(e.target);
    let row = switchStateButton.parent().parent().parent();
    let state = row.find(".--state").data('state');
    if (state === 'OR') {
      row.find(".--state").data('state', 'AND')
      row.find('.--state select')[0].value = 'AND';
    } else {
      row.find(".--state").data('state', 'OR')
      row.find('.--state select')[0].value = 'OR';
    }
    renderStates();
  }

  function renderStates() {
    let dataRows = $('.composer tbody>tr:not(.template_row):not(.adder_row)')

    if (dataRows.length < 1) {
      return
    }
    dataRows.first().find('.group_cell.--or button').addClass('--hidden')
    dataRows.first().find('.group_cell.--and button').addClass('--hidden')
    dataRows = dataRows.slice(1, dataRows.length)
    dataRows.each(function () {
      let state = $(this).find('.--state').data('state')
      if (state === 'OR') {
        $(this).find('.group_cell.--or button').removeClass('--hidden')
        $(this).find('.group_cell.--and button').addClass('--hidden')
      } else if (state === 'AND') {
        $(this).find('.group_cell.--or button').addClass('--hidden')
        $(this).find('.group_cell.--and button').removeClass('--hidden')
      }
    })
  }

  function updateElementIndex(el, ndx) {
    const id_regex = new RegExp("(" + prefix + "-(\\d+|__prefix__))");
    const replacement = prefix + "-" + ndx;
    if ($(el).prop("for")) {
      $(el).prop("for", $(el).prop("for").replace(id_regex, replacement));
    }
    if (el.id) {
      el.id = el.id.replace(id_regex, replacement);
    }
    if (el.name) {
      el.name = el.name.replace(id_regex, replacement);
    }
  }

  let addButton = $(".composer tr.adder_row button");
  let deleteButtons = $('.composer .delete_button');
  let switchStateButtons = $('.composer .group_cell button')
  addButton.on("click", addRowHandler)
  deleteButtons.each(function () {
    $(this).on("click", deleteRowHandler)
  })
  switchStateButtons.each(function () {
    $(this).on("click", switchStates)
  })

}

function setForeignKeyInterpreter() {

  function refreshValueInput(e) {



    e.preventDefault();
    let attributeSelect = $(e.target)[0];
    let rowNumber = /id_form-(\d*)/g.exec(attributeSelect.id)[1];
    let baseModel = metadata.find(model => model.name === 'PushToken');
    let descriptors = attributeSelect.value.split('__');

    let currentModel = baseModel;
    let prevModel;
    let currentField;

    for (let descriptor of descriptors) {
      currentField = currentModel.fields.find(field => field.name === descriptor);
      prevModel = currentModel;
      currentModel = metadata.find(model => model.name === currentField.attributes.to);
    }

    if (currentField.type === 'foreign-key') {
      let selectWidget = showValueSelect(rowNumber);
      fillChoicesValueSelect(selectWidget, prevModel, currentField)
    } else {
      showValueInput(rowNumber);
    }
  }

  function fillChoicesValueSelect(selectWidget, model, descriptor) {

    let objectsList = [];
    fetch(`../../fetcher?model_name=${model.name}&field_name=${descriptor.name}`)
      .then(res => res.json())
      .then(json => {objectsList = json.results})
      .then(() => {
        selectWidget.clearChildren();
        for (let object of objectsList) {
          let opt = document.createElement('option')
          opt.value = object.key
          opt.innerHTML = object.name
          selectWidget.appendChild(opt)
        }
      }
    )
  }

  function showValueSelect(rowNumber) {
    let inputWidget = $(`.composer [id$='value'][id^='id_form-${rowNumber}']`)
    let selectWidget = $(`.composer [id$='value_select'][id^='id_form-${rowNumber}']`)
    inputWidget.value = "";
    inputWidget.addClass('--hidden')
    selectWidget.removeClass('--hidden')

    return selectWidget[0]
  }

  function showValueInput(rowNumber) {
    let inputWidget = $(`.composer [id$='value'][id^='id_form-${rowNumber}']`)
    let selectWidget = $(`.composer [id$='value_select'][id^='id_form-${rowNumber}']`)
    selectWidget.value = "";
    selectWidget.addClass('--hidden')
    inputWidget.removeClass('--hidden')
  }

  fetch('../../metadata')
    .then(res => res.json())
    .then(json => {metadata = json.results})

  let attributeFields = $(".composer [id$='attribute']");
  attributeFields.each(function () {
    $(this).on("change", refreshValueInput)
  })

}

$(document).ready(function() {
  formset()
  setForeignKeyInterpreter()
});
