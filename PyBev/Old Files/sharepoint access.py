import sharepoint as sp

server_url = r'https://markettrackllc.sharepoint.com/'
#Team Action Items
site_url = server_url + r'sites/SolonAdOps/Team%20Sites/coverage&collections/Lists/Team%20Action%20Items/allitems.aspx'

#Documents (this is where BAM lives)
site_url = server_url + r'sites/SolonAdOps/Team%20Sites/coverage%26collections/Shared%20Documents/Forms/AllItems.aspx?viewpath=%2Fsites%2FSolonAdOps%2FTeam%20Sites%2Fcoverage%26collections%2FShared%20Documents%2FForms%2FAllItems.aspx'
username = 'sroy'
pw = '''het4W8<U'''

opener = sp.basic_auth_opener(server_url, username, pw)

site = sp.SharePointSite(site_url, opener)

for sp_list in site.lists:
    print(sp_list.id, sp_list.meta['Title'])