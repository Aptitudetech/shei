## SHEI

Module for SHEI

#### License

MIT

### Release


#### November 2019
* New fields
    * Delivery Note-eta_date
        * The date when the customer is supposed to have received his package
    * Delivery Note-is_special_shipping
        * A checkbox to determine if the shipping is special. Ie, the employee have write the reasons in the comments
    * Address-state_per_country
        * When selected, it will overwrite the country and the state of the Address
    * Project-ready_for_production_date
        * The date when the package is ready for production
    * Quotation Item-reference_panel
        * The item is linked to an item in panel_list. This field helps us determine to which item it correspond. 
        **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-measurement
        * Determine the measurement of the panel. It can be 'MM', 'Inches', 'CM', 'Foot'
        **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-quotation_mode
        * Determine if the Quotation will contains panel(Price Configurator) or not (Standard)
    * Quotation-total_folds
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-total_holes
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-total_tools
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-total_av_nuts
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-total_studs
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-sample_without_order_qty
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-sample_with_order_qty
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-number_of_files
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-technical_drawing_hours
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-have_technical_drawing
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-graphic_design_nb_hours
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-have_graphic_design
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-nb_colour_to_match
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-need_colour_match
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-have_matching_mural
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 
    * Quotation-panel_list
        * **Only applicable when the Quotation Mode is set to 'Price Configurator'** 

* New Reports
    * Sommaire Journalier
        * Display all Delivery Note that should be delivered today and are not 'Completed'
    * SH Budget Variance Report
         *Display the original 'Budget Variance Report', but the amount have been formatted correclty. 
    * SO Work Order Status
        * Display all SO Work Order with the Project Status
    
* New/Modified Document
    * Item
        * Set Maintain Stock to false by default
    * Price Configurator Setting
    * Price Configurator Item
    * States per Country
        * Set a State with a Country following a convention
    * SO Work Order Item
    * SO Work Order
    * Dropdown Options
        * Set some value for the Price Configurator
    * Preflight Review
        * The client can send us his Preflight Review using the Customer Portal. It will send a copy in the ERP and an employee can accept or reject what the client have entered with some Notes to help him change the data he previously entered
    * Preflight Item
    * Dynamic SO Work Order
    
* Print Format
    * shei - Delivery Note
        * add image beside description
    * shei - SO Work Order
        * add image beside description
    * shei - All Shipping Information
        * Display all information concerning the shipping

* Other
    * In the Address doctype, the country is now empty by default and the user must select something in the field 'Country by State'. By doing this, it will automatically filed the country and the state. 
        * Reason: because of a new US law, we need to have the right state for each address, which is not the case currently. Also, it will allow all the data to be conform and to be search more easily.
    * The quotation will now have a 'Quotation mode'. When 'Price Configurator' is selected, a whole new section will appear (See 'New Field' section for the list). 

#### 31 May 2019
* New field 
    * absolute_end_date in Project. Restricted to "Projects Manager" only
    * have_dock in Address
    * is_residential in Address
    * restricted_to_role in Project -> restrict the project to the specified role
    * hts_name in Item

* Modify Report 
    * 'First Open Task by Open Project' -> Role "Projects Manager" have the field absolute_end_date in the report

* Delete old Reports
    * Accounts Payable Summary SHEI
    * Accounts Payable Summary US SHEI
    * Accounts Receivable Summary SHEI
    * Accounts Receivable Summary US SHEI

* New Document
    * Company Stats: Display some financial data (Sales te, Receivable/payable Account, ... for curr month, year and date)
    * Crate Information
    * Shipping Company
    * Doc gain per Sales Person (child table for Company Stats)

* Print Format
    * shei - Bill Of Lading
    * shei - Commercial Invoice
    * SHEI - SO Work Order

* Updated Document
    * SO Work Order Item -> height/width are 0 by default
    * Project -> Shipping Information section
        * Third Party shipper
        * Waybill
        * Shipping Company
        * Table with Crate Information