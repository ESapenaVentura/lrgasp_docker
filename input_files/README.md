### How to generate the static checksums
(**Apply this procedure ONLY if static files are changed**)
```bash
cd input_files/static
md5 * > ../../lrgasp_validation/static_md5_list.txt
git add ../../lrgasp_validation/static_md5_list.txt
git commit -m "Updated static md5 list"
git push
```