

def sort_duigui(user_id, article_id, o_id=None):
    datadict = []
    if o_id:
        objs = models.zgld_article_to_customer_belonger.objects.filter(customer_parent_id=o_id).filter(
            article_id=article_id).filter(user_id=user_id)

        for obj in objs:
            if obj.customer_parent.id == obj.customer.id:
                continue

            username = str(decode_username, 'utf-8')
            parentId = obj.customer.id
            result = init_data(user_id, article_id, parentId)
            flag = True

            # print('result=====> ',result)
            for other in datadict:
                if username in other.get('name'):
                    flag = False
                    if result:
                        print(result)
                        other.get('children').append(result[0])
            if flag:
                if result:
                    datadict.append({
                        'name':username,
                        'children': result
                    })
                else:
                    datadict.append({
                        'name': username,
                    })

    return datadict
