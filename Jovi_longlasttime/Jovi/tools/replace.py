import os



rep_content = 'var fo = createPlayer("v_player",540,400);fo.addVariable("videoId","vid");fo.addVariable("videoCenterId","7de6573d3a1b47ea8f2731e6eb7aa471");fo.addVariable("videoType","0");fo.addVariable("videoEditMode","1");fo.addVariable("isAutoPlay","true");fo.addVariable("tai","news");fo.addVariable("languageConfig","");fo.addParam("wmode","opaque");writePlayer(fo,"embed_playerid");'
for i in os.listdir('E:\\数据存储文档\\定期更新12-3\\大搜狐网\\动漫'):
    for j in os.listdir('E:\\数据存储文档\\定期更新12-3\\大搜狐网\\动漫\\%s' % i):
        with open('E:\\数据存储文档\\定期更新12-3\\大搜狐网\\动漫\\%s\\%s' % (i,j),'r+',encoding='utf-8') as f:
            content = ''.join(f.readlines())
            content = content.replace('rep_content','')
            f.seek(0,0)
            f.write(content)
