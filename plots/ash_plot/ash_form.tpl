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



<form action="ash" method="post" enctype="multipart/form-data" id="ashform">

<fieldset>

    <div class="form_row">

        <div class="form_property form_required">{{! form.data.label }}:</div> 
        <div class="form_property form_required">{{! form.data(cols=30, rows=30) }}
            %field_errors(form.data.errors)
        </div>
            <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.xlabel.label }}: {{! form.xlabel() }}
            %field_errors(form.xlabel.errors)
        </div>
        <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.color.label }}:&nbsp; 
            <input type="color" name="{{form.color.id}}" id="{{form.color.id}}" label="{{form.color.label.text}}" value="{{form.color.data}}" />
            %field_errors(form.color.errors) 
        </div>
        <div class="clearer">&nbsp;</div>
        <div class="form_value">{{! form.fill_color.label }}:&nbsp; 
            <input type="color" name="{{form.fill_color.id}}" id="{{form.fill_color.id}}" label="{{form.fill_color.label.text}}" 
                    value="{{form.fill_color.data}}" />
            %field_errors(form.fill_color.errors) 
        </div>
        <div class="clearer">&nbsp;</div>
    </div>
    <input type="hidden" name="filled" value="good">
    <div class="form_row form_row_submit">

        <div class="form_value">
            <input type="submit" name="submit" class="button" value="Make ASH">
            
            <input type="submit" name="png_download" id="png_download" class="hidden" />
            
            <input type="submit" name="svg_download" id="svg_download" class="hidden" />

		    <input type="submit" name="clear" class="button" value="Clear the Form"></div>

		    <div class="clearer">&nbsp;</div>

	    </div>

    </fieldset>

</form>
