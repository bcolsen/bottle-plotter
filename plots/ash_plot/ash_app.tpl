%#template for editing a task
%#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item

%include('header.tpl')
<h2>ASH Plotter</h2>
<h3>Average Shifted Histograms (ASH) in your browser</h3>
    <div id="colwrapper">
        <div id="leftcolumn">
            <h3>Copy in your data and fill in test info...</h3>

            % include('ash_form.tpl',form=form)

            
        </div>
        <div id="rightcolumn">
            %if (filled == 'good'):
                <img class="plot" src="data:image/png;base64,{{img}}" alt="ASH Plot" width=600 align="center"/>
                <div id="chart_export"><h3>Download Full Resolution Charts...</h3>
                    <a href="#"><label style="cursor:pointer" for="png_download">Download PNG</label></a> (300 dpi ready for publication)<br />
                    <!--<a href="png?type=pdf">Download PDF</a><br />-->
                    <a href="#"><label style="cursor:pointer" for="svg_download">Download SVG</label></a> (Edit this for free in <a href="https://www.inkscape.org/">Inkscape</a>.)<br />
                </div>
            %end
        </div>
    </div>
</div>

    

