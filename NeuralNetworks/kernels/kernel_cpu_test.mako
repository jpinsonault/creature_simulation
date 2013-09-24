__kernel void test()
{
  
  printf("GID: %d\n", get_global_id(0));
  
}