

navy_query_config = [
        """SELECT typeID  FROM [eve.SDEmount.full.09202024].[dbo].[publishedShips0924] 
            where marketGroupName like 'Navy Faction'""",
        'localhost',
        'eve.SDEmount.full.09202024',
        'publishedShips0924'
    ]

pirate_query_config = [
        """SELECT typeID  FROM [eve.SDEmount.full.09202024].[dbo].[publishedShips0924] 
            where marketGroupName like 'Pirate Faction'""",
        'localhost',
        'eve.SDEmount.full.09202024',
        'publishedShips0924'
    ]




