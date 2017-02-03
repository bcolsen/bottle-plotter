%def render_field(field, desc=None, **kwargs): # simple validation
<input type="text" name="{{field.id}}" id="{{field.id}}" label="{{field.label.text}}" value="{{field.label.text}}" />
   %if field.errors:
      %if desc:
         {{!desc}}
      %end
      <ul class=errors>
      %for error in field.errors:
         <li>{{ error }}</li>
      %end
      </ul>
   %end
%end

%def field_errors(errors):
    %if errors:
        <ul class="errors">
        %for error in errors:
            <li>{{ error }}</li>
        %end
        </ul>
    %end
%end



<form action="ce" method="post" enctype="multipart/form-data" id="ceform">

<fieldset>

    <div class="form_row">
        <div class="two-col">
            <lable>Data copied from a table or separated by commas (2 to 100000 points):</label>
            <div class="clearer">&nbsp;</div>
            <div class="col1">
                <div class="form_property form_required">{{! form.x_data.label }}</div> 
                <div class="form_property form_required">{{! form.x_data(cols=17, rows=25) }}
                    %field_errors(form.x_data.errors)
                </div>
            </div>
            <div class="col2">
                <div class="form_property form_required">{{! form.y_data.label }}</div> 
                <div class="form_property form_required">{{! form.y_data(cols=17, rows=25) }}
                    %field_errors(form.y_data.errors)
                </div>
            </div>
        </div>
        <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.x_label.label }}: {{! form.x_label() }}
            %field_errors(form.x_label.errors)
        </div>
        <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.y_label.label }}: {{! form.y_label() }}
            %field_errors(form.y_label.errors)
        </div>
        <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.color.label }}:&nbsp; 
            <input type="color" name="{{form.color.id}}" id="{{form.color.id}}" label="{{form.color.label.text}}" 
                    value="{{form.color.data}}" />
            %field_errors(form.color.errors) 
        </div>
        <div class="clearer">&nbsp;</div>
    </div>
    <input type="hidden" name="filled" value="good">
    <div class="form_row form_row_submit">

        <div class="form_value">
            <input type="submit" name="submit" class="button" value="Plot CE">
            
            <input type="submit" name="png_download" id="png_download" class="hidden" />
            
            <input type="submit" name="svg_download" id="svg_download" class="hidden" />

		    <input type="submit" name="clear" class="button" value="Clear the Form"></div>

		    <div class="clearer">&nbsp;</div>

	    </div>

    </fieldset>

</form>
