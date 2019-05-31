## SHEI

Module for SHEI

#### License

MIT

### Release

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