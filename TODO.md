* DONE add customer sales periods to skeletal cms
* DONE add option for multiple tables to model display
* DONE add import form excel, frontend???
* DONE add backend script for house keeping - eg. creating periods and populating them
* DONE add excel output
* DONE add front end import
* DONE fix problem with import not generating sales periods
* think about renaming SKUSales
* use id instead of xl_id
* DONE make sure everyting is working and freeze at v0.1
* DONE exlcude some fields from display
* DONE fix breadcrumbs
* DONE correct index title from markets trace
* DONE rename whole thing to ignore child`s farm and become brand less (extra file of customer settings?)
* add front page showing summary incomplete things
* DONE calculate sales estimates
* DONE think about how sales periods are generated with import
* DONE get heavy lifting done separately
* DONE do estimation in c++???
* DONE update skeletaldisplay README
* DONE set secure passwords
* DONE use bootstrap to prettify things
* DONE use handsontable to create clientside tables with django-rest-framework
* DONE create/find favicon
* DONE setup django authentication
* add account settings page and script to create users?? http://docs.django-userena.org/en/latest/index.html
* DONE setup script to move to server straight from github
* add function to remove spaces from above
* DONE possibly split ExcelImportExport right off, with handsontable(??) - probably not, leave excel as backend output
* DONE add suppliers
* DONE add sku groups
* DONE add seasonal variation instances
* DONE add sales rate factor to customers
* DONE changed models to process, add tabs
* DONE include instructions on index page.
* DONE process in three(?) steps
* DONE add promotion instances - containing skus, customers, start/finish dates
* confirm forcasts
* DONE add output: sku
* add output: sku group
* DONE orders required
* test calculation completely to check it`s right
* use numeral.js for formatting values in display page
* add "paste mode" to django-hot
* DONE edit templates so HOT works with multiple tags in the same page
* DONE set sales to be double not int
* DONE use external module for import/export
* DONEfix and test Imex
* DONE group orders and account for discount (remember minimum order)
* DONE get lead time to work properly
* DONE get formsets working properly in all add/edit pages - 
    * under each item (eg. customer) have buttons for mass edit of associated items - eg. customer-sku-info or customer-sales-periods only requires "add new item" feature as through can be defined a for all manytomany relationships
    * use - http://www.hoboes.com/Mimsy/hacks/replicating-djangos-admin/
* DONE add buttons for simple relationships
* consider cleaning up simple button save - move save into SimpleHandsontableDisplay
* DONE get rid of "save required" message after cancelling sub change on hands on table
* DONE? correct reload button on extra hot
* DONE (ish) get _add_modify to use bulk edit/add
* DONE call worker on customer update etc.
* DONE set some columns to readonly on hot
* DONE add buttons to hot form edit page
* fix crums - make shorter and prevent repeats
* allow for comments above extra hot eg. "leave blank to use default"
* add "changes will be lost" prompt on exiting edited extra hot
* move edit buttons to be next to tables
* DONE add "calculate" button and make it green with after_save
* DONE output excel report
* generated json in c++, add "loading" twirl on chart pages
* add more charts

### Later

* change imex to use bulkcreate where there are no related items
* combine hot and skeletal


problem with calculating orders/lead times - if demand is based on order group assembly and customer are not known therefore can`t calculate lead time based on them

solution is to add lead time to demand then use that to calculate order date for orders.

Possible future problem - components associated with an order group may not all have the same price. 
