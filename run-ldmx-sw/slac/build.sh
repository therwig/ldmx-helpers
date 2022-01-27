cd ../build
#cmake -DGeant4_DIR=$G4DIR -DROOT_DIR=$ROOTDIR -DXercesC_DIR=$XercesC_DIR -DCMAKE_INSTALL_PREFIX=../install ..
cmake --build . --target install -- -j8
cd ../run
